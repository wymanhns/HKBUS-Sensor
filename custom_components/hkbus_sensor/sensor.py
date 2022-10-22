import asyncio
from datetime import timedelta
import datetime
import logging
import aiohttp
import json
import jmespath
from dateutil.parser import parse

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

import xml.etree.ElementTree as ET

REQUIREMENTS = [ ]

_LOGGER = logging.getLogger(__name__)

CONF_ATTRIBUTION = "Data provided by Open API"
CONF_STOPID = 'stop_id'
CONF_ROUTENUMBER = 'route_number'
CONF_APIKEY = 'api_key'
CONF_BUSDIR = 'busdir'

DEFAULT_NAME = 'HK Bus Sensor'
DEFAULT_ICON = 'mdi:bus-clock'
                    
SCAN_INTERVAL = timedelta(seconds=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_STOPID): cv.string,
    vol.Required(CONF_ROUTENUMBER): cv.string,
    vol.Optional(CONF_APIKEY): cv.string,
    vol.Optional(CONF_BUSDIR, default=CONF_BUSDIR): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    _LOGGER.debug("start async setup platform")

    name = config.get(CONF_NAME)
    stopid = config.get(CONF_STOPID)
    routenumber = config.get(CONF_ROUTENUMBER)
    apikey = config.get(CONF_APIKEY)
    busdir = config.get(CONF_BUSDIR)
    res_list = 'x'
    session = async_get_clientsession(hass)
    
    async_add_devices(
        [HkBusSensor(name, stopid, routenumber, apikey, busdir)],update_before_add=True)
    
class HkBusSensor(Entity):

    def __init__(self, name, stopid, routenumber, apikey, busdir):
        """Initialize the sensor."""
        #_LOGGER.warning('插件初始')
        self._name = name
        self._stopid = stopid
        self._routenumber = routenumber
        self._apikey = apikey
        self._busdir = busdir
        self._state = None
        self._icon = DEFAULT_ICON

    @property
    def extra_state_attributes(self):
        #_LOGGER.warning('輪出 ' + self._data)
        attr = {}

        json_data = json.loads(self._data)
        
        find1 = jmespath.search('data[?dir==`'  + self._busdir + '`]' ,json_data)
        #_LOGGER.warning('比對結果 : ' + str(len(find1)))

        attr["route_number"] = self._routenumber
        attr["stop_id"] = self._stopid
        
        nowtime=str(datetime.datetime.strptime(str(datetime.datetime.now())[0:19],'%Y-%m-%d %H:%M:%S'))
        Rnowtime = parse(str(nowtime))
        
        attr["icon"] = 'mdi:bus-clock'

        #_LOGGER.warning('state更新 ' + str(find1[0]['rmk_tc']))
        attr["rmk_tc"] = str(find1[0]['rmk_tc'])

        if len(find1) == 3 :
            Ltime1=datetime.datetime.strptime(str(find1[0]['eta'][0:19]),'%Y-%m-%dT%H:%M:%S')
            RLtime1 = parse(str(Ltime1))            
            Ltime2=datetime.datetime.strptime(str(find1[1]['eta'][0:19]),'%Y-%m-%dT%H:%M:%S')
            Ltime3=datetime.datetime.strptime(str(find1[2]['eta'][0:19]),'%Y-%m-%dT%H:%M:%S')
            attr["buses_1"] = str(Ltime1)[11:16]
            attr["buses_2"] = str(Ltime2)[11:16]
            attr["buses_3"] = str(Ltime3)[11:16]
        elif len(find1) == 2 :
            Ltime1=datetime.datetime.strptime(str(find1[0]['eta'][0:19]),'%Y-%m-%dT%H:%M:%S')
            RLtime1 = parse(str(Ltime1)) 
            Ltime2=datetime.datetime.strptime(str(find1[1]['eta'][0:19]),'%Y-%m-%dT%H:%M:%S')
            attr["buses_1"] = ''
            attr["buses_2"] = str(Ltime1)[11:16]
            attr["buses_3"] = str(Ltime2)[11:16]
        elif len(find1) == 1 :
            try:
                Ltime1=datetime.datetime.strptime(str(find1[0]['eta'][0:19]),'%Y-%m-%dT%H:%M:%S')
                RLtime1 = parse(str(Ltime1)) 
                attr["buses_3"] = str(Ltime1)[11:16]
            except:
                attr["buses_3"] = '尾班已開出'
                attr["icon"] = 'mdi:timer-off-outline' #'mdi:bus-alert'
                self._state = 0
            attr["buses_1"] = ''
            attr["buses_2"] = ''
        #_LOGGER.warning('state更新 ' + str(find1[0]['dest_en']))
        try:
            countdowntimes = round((RLtime1 - Rnowtime).total_seconds() // 60 )
            if countdowntimes < 0 :
                countdowntimes = 0
        except:
            countdowntimes = 0
            
        attr["next_bus_countdown"] = countdowntimes
        
        return attr

    async def asyncGet(self,url,header):
        #_LOGGER.warning('更新url :' + url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                #_LOGGER.warning('res : ' + str(response.status))
                html = await response.json()
                #_LOGGER.warning('更新url END' )
            return html

    async def yunmi_login(self):
        #_LOGGER.warning('yunmi login to update  ')
        #url="http://data.etabus.gov.hk/v1/transport/kmb/eta/26AC2D471648CA0C/43A/1"
        url="http://data.etabus.gov.hk/v1/transport/kmb/eta/" + self._stopid + "/" + self._routenumber + "/1"
        self._name = 'HK BUS ' + self._routenumber
        headers="1"
        #_LOGGER.warning('敗 yunmi url : ' + url)
        res_list = await self.asyncGet(url,headers)
        #_LOGGER.warning('yunmi login to update END ')
        return res_list

    @asyncio.coroutine
    async def async_update(self):
        #_LOGGER.warning('Async_update')
        res_list = await self.yunmi_login()
        self._data = json.dumps(res_list)
        #_LOGGER.warning('Async_update END : ' )    
        
        return self._state

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state
