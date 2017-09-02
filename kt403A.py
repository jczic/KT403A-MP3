
from machine import UART
from utime   import sleep_ms
from ustruct import unpack

class KT403A :

    # ============================================================================
    # ===( Constants )============================================================
    # ============================================================================

    DEVICE_U_DISK = 1
    DEVICE_SD     = 2
    DEVICE_AUX    = 3
    DEVICE_SLEEP  = 4
    DEVICE_FLASH  = 5

    EQ_NORMAL     = 0
    EQ_POP        = 1
    EQ_ROCK       = 2
    EQ_JAZZ       = 3
    EQ_CLASSIC    = 4
    EQ_BASS       = 5

    # ============================================================================
    # ===( Constructor )==========================================================
    # ============================================================================

    def __init__( self,
                  uartBus,
                  txPinNum,
                  rxPinNum,
                  device    = None,
                  volume    = 70,
                  eq        = None ) :
        txPinId = "P" + str(txPinNum)
        rxPinId = "P" + str(rxPinNum)
        self._uart = UART( uartBus,
                           baudrate = 9600,
                           bits     = 8,
                           parity   = None,
                           stop     = 1,
                           pins     = (txPinId, rxPinId, None, None) )
        self.SetDevice(device if device else KT403A.DEVICE_SD)
        if not self.GetState() :
            raise Exception('KT403A could not be initialized.')
        self.SetVolume(volume)
        self.SetEqualizer(eq if eq else KT403A.EQ_NORMAL)

    # ============================================================================
    # ===( Utils )================================================================
    # ============================================================================

    def _txCmd(self, cmd, dataL=0, dataH=0) :
        self._uart.write(b'\x7E')        # Start
        self._uart.write(b'\xFF')        # Firmware version
        self._uart.write(b'\x06')        # Command length
        self._uart.write(bytes([cmd]))   # Command word
        self._uart.write(b'\x00')        # Feedback flag
        self._uart.write(bytes([dataH])) # DataH
        self._uart.write(bytes([dataL])) # DataL
        self._uart.write(b'\xEF')        # Stop
        sleep_ms(200 if cmd == 0x09 else 1000 if cmd == 0x0C else 30)

    # ----------------------------------------------------------------------------

    def _rxCmd(self) :
        if self._uart.any() :
            buf = self._uart.read(10)
            if buf is not  None and \
               len(buf) ==   10 and \
               buf[0]   == 0x7E and \
               buf[1]   == 0xFF and \
               buf[2]   == 0x06 and \
               buf[9]   == 0xEF     :
               cmd  = buf[3]
               data = unpack('>H', buf[5:7])[0]
               return (cmd, data)
        return None

    # ----------------------------------------------------------------------------

    def _readLastCmd(self) :
        res = None
        while True :
            r = self._rxCmd()
            if not r :
                return res
            res = r

    # ============================================================================
    # ===( Functions )============================================================
    # ============================================================================

    def PlayNext(self) :
        self._txCmd(0x01)

    # ----------------------------------------------------------------------------

    def PlayPrevious(self) :
        self._txCmd(0x02)

    # ----------------------------------------------------------------------------

    def PlaySpecific(self, trackIndex) :
        self._txCmd(0x03, int(trackIndex%256), int(trackIndex/256))

    # ----------------------------------------------------------------------------

    def VolumeUp(self) :
        self._txCmd(0x04)

    # ----------------------------------------------------------------------------

    def VolumeDown(self) :
        self._txCmd(0x05)

    # ----------------------------------------------------------------------------

    def SetVolume(self, percent) :
        if percent < 0 :
            percent = 0
        elif percent > 100 :
            percent = 100
        self._txCmd(0x06, int(percent*0x1E/100))

    # ----------------------------------------------------------------------------

    def SetEqualizer(self, eq) :
        if eq < 0 or eq > 5 :
            eq = 0
        self._txCmd(0x07, eq)

    # ----------------------------------------------------------------------------

    def RepeatCurrent(self) :
        self._txCmd(0x08)

    # ----------------------------------------------------------------------------

    def SetDevice(self, device) :
        self._device = device
        self._txCmd(0x09, device)

    # ----------------------------------------------------------------------------

    def SetLowPowerOn(self) :
        self._txCmd(0x0A)

    # ----------------------------------------------------------------------------

    def SetLowPowerOff(self) :
        self.SetDevice(self._device)

    # ----------------------------------------------------------------------------

    def ResetChip(self) :
        self._txCmd(0x0C)

    # ----------------------------------------------------------------------------

    def Play(self) :
        self._txCmd(0x0D)

    # ----------------------------------------------------------------------------

    def Pause(self) :
        self._txCmd(0x0E)

    # ----------------------------------------------------------------------------

    def PlaySpecificInFolder(self, folderIndex, trackIndex) :
        self._txCmd(0x0F, trackIndex, folderIndex)

    # ----------------------------------------------------------------------------

    def EnableLoopAll(self) :
        self._txCmd(0x11, 1)

    # ----------------------------------------------------------------------------

    def DisableLoopAll(self) :
        self._txCmd(0x11, 0)

    # ----------------------------------------------------------------------------

    def PlayFolder(self, folderIndex) :
        self._txCmd(0x12, folderIndex)

    # ----------------------------------------------------------------------------

    def Stop(self) :
        self._txCmd(0x16)

    # ----------------------------------------------------------------------------

    def LoopFolder(self, folderIndex) :
        self._txCmd(0x17, folderIndex)

    # ----------------------------------------------------------------------------

    def RandomAll(self) :
        self._txCmd(0x18)

    # ----------------------------------------------------------------------------

    def EnableLoop(self) :
        self._txCmd(0x19, 0)

    # ----------------------------------------------------------------------------

    def DisableLoop(self) :
        self._txCmd(0x19, 1)

    # ----------------------------------------------------------------------------

    def EnableDAC(self) :
        self._txCmd(0x1A, 0)

    # ----------------------------------------------------------------------------

    def DisableDAC(self) :
        self._txCmd(0x1A, 1)

    # ----------------------------------------------------------------------------

    def GetState(self) :
        self._txCmd(0x42)
        r = self._readLastCmd()
        return r[1] if r and r[0] == 0x42 else None

    # ----------------------------------------------------------------------------

    def GetVolume(self) :
        self._txCmd(0x43)
        r = self._readLastCmd()
        return int(r[1] / 0x1E *100) if r and r[0] == 0x43 else 0

    # ----------------------------------------------------------------------------

    def GetEqualizer(self) :
        self._txCmd(0x44)
        r = self._readLastCmd()
        return r[1] if r and r[0] == 0x44 else 0

    # ----------------------------------------------------------------------------

    def GetFilesCount(self, device=None) :
        if not device :
            device = self._device
        if device == KT403A.DEVICE_U_DISK :
            self._txCmd(0x47)
        elif device == KT403A.DEVICE_SD :
            self._txCmd(0x48)
        elif device == KT403A.DEVICE_FLASH :
            self._txCmd(0x49)
        else :
            return 0
        sleep_ms(200)
        r = self._readLastCmd()
        return r[1] if r and r[0] >= 0x47 and r[0] <= 0x49 else 0

    # ----------------------------------------------------------------------------

    def GetFolderFilesCount(self, folderIndex) :
        self._txCmd(0x4E, folderIndex)
        sleep_ms(200)
        r = self._readLastCmd()
        return r[1] if r and r[0] == 0x4E else 0

    # ----------------------------------------------------------------------------

    def IsStopped(self) :
        return self.GetState() == 0x0200

    # ----------------------------------------------------------------------------

    def IsPlaying(self) :
        return self.GetState() == 0x0201

    # ----------------------------------------------------------------------------

    def IsPaused(self) :
        return self.GetState() == 0x0202

    # ============================================================================
    # ============================================================================
    # ============================================================================
