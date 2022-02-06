[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
# HK BUS Sensor HK KMB Bus

This is home assistant custom component to pull bus times from Open API.  This is pretty limited right now, simply pulling in the next three times for a given stop and route.

There is a lovelace ui custom card available here: https://github.com/wymanhns/hkbus-card

已成功修改試用中
```
# 數據資料
九龍巴士及龍運巴士路線實時到站數據 https://data.gov.hk/tc-data/dataset/hk-td-tis_21-etakmb
```
### Manual Installation

Copy this folder to `<config_dir>/custom_components/hkbus_sensor/`.

### HACS Custom Install

1. Go to the community tab of your home assistant installation
2. Click settings
3. Add "https://github.com/wymanhns/HKBUS-Sensor" with the type **Integration**
4. Click Save
5. Restart home assistant

### Usage

Add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
# 巴士站ID 從網址 https://data.etabus.gov.hk/v1/transport/kmb/stop 中尋找巴士站名如下 
#   {"stop":"26AC2D471648CA0C","name_en":"CHEUNG WANG BUS TERMINUS","name_tc":"長宏巴士總站","name_sc":"长宏巴士总站","lat":"22.357309","long":"114.096206"}
#   這"stop":"26AC2D471648CA0C" 就是
#
# 再去網址： https://data.etabus.gov.hk/v1/transport/kmb/stop-eta/{stop_id}  查看一下是否正確 有沒有你需要的路線 {stop_id} 要填上巴士站ID
#   注 : 同一個地點的巴士站 有機會不只一個 ID 所以要自己去找下有沒有你需要的路線!
# 如 https://data.etabus.gov.hk/v1/transport/kmb/stop-eta/26AC2D471648CA0C 這 "route":"43A" 巴士號就是 43A
#   {"type":"StopETA","version":"1.0","generated_timestamp":"2022-02-06T14:51:39+08:00","data":[{"co":"KMB","route":"43A","dir":"O","service_type":1,"seq":1,
#   "dest_tc":"石籬(大隴街)","dest_sc":"石篱(大陇街)","dest_en":"SHEK LEI (TAI LOONG STREET)","eta_seq":1,"eta":"2022-02-06T14:51:00+08:00","rmk_tc":"原定班次",
#   "rmk_sc":"原定班次","rmk_en":"Scheduled Bus","data_timestamp":"2022-02-06T14:51:13+08:00"},{"co":"KMB","route":"43A","dir":"I","service_type":1,"seq":19,
#   "dest_tc":"青衣(長宏邨)","dest_sc":"青衣(长宏邨)","dest_en":"TSING YI (CHEUNG WANG ESTATE)","eta_seq":1,"eta":"2022-02-06T14:56:40+08:00",
#   "rmk_tc":"","rmk_sc":"","rmk_en":"","data_timestamp":"2022-02-06T14:51:13+08:00"}]}
#
# 巴士方向 "dir":"O" 有 "O" 或 "I" 要填在 busdir 如上例中 43A "O" 方向是 "dest_tc":"石籬(大隴街)" , "I" 方向是 "dest_tc":"青衣(長宏邨)" !

sensor:
  - platform: hkbus_sensor
    stop_id: 26AC2D471648CA0C #巴士站ID
    busdir: O # 方向 
    route_number: 43A #巴士號

  - platform: hkbus_sensor
    stop_id: 79842A7E2FC0844F
    busdir: O
    route_number: 42M
    
# 設置完要重啟,重啟之後會多了 sensor.hk_bus_43a
#     route_number: 43A
#     stop_id: 26AC2D471648CA0C
#     icon: mdi:bus-clock
#     rmk_tc: 原定班次
#     buses_1: '15:39'
#     buses_2: '15:51'
#     buses_3: '16:03'
#     next_bus_countdown: 9
#    friendly_name: HK BUS 43A
#
```

