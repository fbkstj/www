// 自行車「後方來車」警示：ESP32 燈號與蜂鳴器
// 電腦每 0.2 秒傳一次警示等級：L0＝安全、L1＝注意、L2＝危險
// 超過 OFFLINE_MS 沒收到 → 離線（綠燈慢閃），提醒「警示系統沒有在運作」
// 開發板選「ESP32 Dev Module」，不需要額外程式庫

const int PIN_GREEN  = 25;
const int PIN_YELLOW = 26;
const int PIN_RED    = 27;
const int PIN_BUZZER = 14;   // 主動式蜂鳴器模組，HIGH＝響

const unsigned long OFFLINE_MS = 1500;

int level = -1;              // -1＝離線
unsigned long lastMsg = 0;
String line;

void setOutputs(bool g, bool y, bool r, bool buzz) {
  digitalWrite(PIN_GREEN, g);
  digitalWrite(PIN_YELLOW, y);
  digitalWrite(PIN_RED, r);
  digitalWrite(PIN_BUZZER, buzz);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_GREEN, OUTPUT);
  pinMode(PIN_YELLOW, OUTPUT);
  pinMode(PIN_RED, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  // 開機自我測試：三個燈與蜂鳴器依序動作
  setOutputs(true, false, false, false);  delay(250);
  setOutputs(false, true, false, false);  delay(250);
  setOutputs(false, false, true, true);   delay(150);
  setOutputs(false, false, false, false);
  Serial.println("I,ready");
}

void readSerial() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      if (line.length() == 2 && line[0] == 'L' && line[1] >= '0' && line[1] <= '2') {
        level = line[1] - '0';
        lastMsg = millis();
      }
      line = "";
    } else if (c != '\r' && line.length() < 8) {
      line += c;
    }
  }
}

void loop() {
  readSerial();
  unsigned long now = millis();
  if (level >= 0 && now - lastMsg > OFFLINE_MS) {
    level = -1;
  }

  switch (level) {
    case 0:   // 安全：綠燈恆亮
      setOutputs(true, false, false, false);
      break;
    case 1:   // 注意：黃燈每 0.25 秒切換，每秒短嗶一次
      setOutputs(false, (now / 250) % 2, false, (now % 1000) < 60);
      break;
    case 2: { // 危險：紅燈快閃，嗶聲 0.1 秒響、0.1 秒停
      bool on = (now / 100) % 2;
      setOutputs(false, false, on, on);
      break;
    }
    default:  // 離線：綠燈每 2 秒閃一下
      setOutputs((now % 2000) < 150, false, false, false);
  }
  delay(10);
}
