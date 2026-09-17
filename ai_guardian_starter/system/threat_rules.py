"""
威脅判斷規則:把 YOLO 每一次的偵測結果轉成「事件」。

每個訊號都要「持續成立一段時間」才算數(SustainedFlag),避免單幀誤判就發警報。

訊號        判斷方式                                           等級
持械        刀/球棒的框與人的框重疊(拿在手上,不是放在桌上)     高
人群奔逃    3 人以上同時快速移動                                高
人員倒地    人的框寬明顯大於高,且持續數秒                       中
異常聚集    人數超過門檻且持續                                  低(只記錄不推播)

限制:COCO 預訓練模型沒有「槍」「火焰」「煙霧」類別,要偵測這些需另外訓練模型。
"""
import math
from dataclasses import dataclass, field

# COCO 類別編號
PERSON = 0
WEAPON_CLASSES = {43: "刀械", 34: "棍棒"}  # knife, baseball bat
# 上課練習用剪刀代替刀械（COCO 76）。正式部署時改成 False，避免把剪刀當成武器。
PRACTICE_SCISSORS = True
if PRACTICE_SCISSORS:
    WEAPON_CLASSES[76] = "剪刀(練習)"

LEVEL_HIGH, LEVEL_MID, LEVEL_LOW = "高", "中", "低"

WEAPON_CONF = 0.35
WEAPON_SUSTAIN_SEC = 0.6
FALL_RATIO = 1.25            # 框寬/框高 超過這個值視為躺臥
FALL_SUSTAIN_SEC = 3.0
CROWD_COUNT = 15
CROWD_SUSTAIN_SEC = 5.0
RUN_SPEED = 0.6              # 每秒移動超過「0.6 個畫面高」算奔跑
RUN_MIN_PEOPLE = 3
RUN_SUSTAIN_SEC = 1.0
GRACE_SEC = 0.8              # 訊號短暫消失的容忍時間(漏偵測一兩幀不重置)


class SustainedFlag:
    def __init__(self, sustain_sec, grace_sec=GRACE_SEC):
        self.sustain_sec = sustain_sec
        self.grace_sec = grace_sec
        self.since = None
        self.last_true = None

    def update(self, now_true, now):
        if now_true:
            if self.since is None:
                self.since = now
            self.last_true = now
        elif self.last_true is not None and now - self.last_true > self.grace_sec:
            self.since = None
            self.last_true = None
        # 用「最後一次真的看到」計算：短暫消失的容忍時間只用來不歸零，不能拿來湊時間
        return self.since is not None and self.last_true - self.since >= self.sustain_sec


@dataclass
class Detection:
    cls: int
    conf: float
    box: tuple  # x1, y1, x2, y2

    @property
    def center(self):
        x1, y1, x2, y2 = self.box
        return (x1 + x2) / 2, (y1 + y2) / 2


@dataclass
class Event:
    kind: str
    level: str
    detail: str
    boxes: list = field(default_factory=list)


def _expand(box, ratio):
    x1, y1, x2, y2 = box
    dw, dh = (x2 - x1) * ratio, (y2 - y1) * ratio
    return x1 - dw, y1 - dh, x2 + dw, y2 + dh


def _overlap(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


class ThreatAnalyzer:
    """每台攝影機一個實例,保存該攝影機的時間狀態。"""

    def __init__(self):
        self.weapon_flag = SustainedFlag(WEAPON_SUSTAIN_SEC)
        self.fall_flag = SustainedFlag(FALL_SUSTAIN_SEC)
        self.crowd_flag = SustainedFlag(CROWD_SUSTAIN_SEC)
        self.run_flag = SustainedFlag(RUN_SUSTAIN_SEC)
        self.prev_centers = []
        self.prev_time = None

    def _running_count(self, people, now, frame_h):
        """用最近鄰配對估算每個人的移動速度(不需額外追蹤套件)。"""
        centers = [p.center for p in people]
        count = 0
        if self.prev_time is not None and self.prev_centers and now > self.prev_time:
            dt = now - self.prev_time
            for cx, cy in centers:
                d = min(math.hypot(cx - px, cy - py) for px, py in self.prev_centers)
                speed = d / frame_h / dt
                if RUN_SPEED < speed < RUN_SPEED * 6:  # 太大多半是配錯人,不算
                    count += 1
        self.prev_centers, self.prev_time = centers, now
        return count

    def analyze(self, dets, now, frame_h):
        people = [d for d in dets if d.cls == PERSON]
        weapons = [d for d in dets if d.cls in WEAPON_CLASSES and d.conf >= WEAPON_CONF]
        events = []

        held = [w for w in weapons
                if any(_overlap(w.box, _expand(p.box, 0.15)) for p in people)]
        if self.weapon_flag.update(bool(held), now):
            names = "、".join(sorted({WEAPON_CLASSES[w.cls] for w in held})) or "武器"
            events.append(Event("持械", LEVEL_HIGH, f"偵測到疑似持有{names}的人員",
                                [w.box for w in held]))

        fallen = [p for p in people
                  if (p.box[2] - p.box[0]) > FALL_RATIO * (p.box[3] - p.box[1])]
        if self.fall_flag.update(bool(fallen), now):
            events.append(Event("倒地", LEVEL_MID, f"{len(fallen) or 1} 人疑似倒地",
                                [p.box for p in fallen]))

        running = self._running_count(people, now, frame_h)
        if self.run_flag.update(running >= RUN_MIN_PEOPLE, now):
            events.append(Event("奔逃", LEVEL_HIGH, f"{running} 人以上同時快速移動,疑似人群逃散"))

        if self.crowd_flag.update(len(people) >= CROWD_COUNT, now):
            events.append(Event("聚集", LEVEL_LOW, f"人數 {len(people)} 人,超過門檻 {CROWD_COUNT}"))

        return events, len(people)
