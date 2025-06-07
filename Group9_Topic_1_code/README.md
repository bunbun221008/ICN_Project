## 程式操作說明
1. 執行 python streaming_server.py --delay 0.0，可依據需要更改delay的時間
2. server 啟動後，會顯示兩個隨機產生的 port 號（分別為 VIDEO 跟 Control 的）
3. 開另一個termianl，執行 python streaming_client.py
4. 輸入 server 的 IP 位址（同一臺電腦是 `127.0.0.1`）以及剛剛 server 顯示的 VIDEO port 號和 CTRL port 號
5. 連線成功後，在 client 視窗可直接輸入下列指令進行即時控制：
- `p` — 播放（開始或繼續傳送影片）
- `t` — 暫停（暫時停止影片傳送）
- `q` — 停止（結束本次串流）
- 完整收到影片後會自動彈出影片，影片播放完會自動關閉。
6. 結束後 client 程式會顯示「啟動延遲」、「傳輸總時長」、「平均吞吐量」等效能資訊於命令列。
