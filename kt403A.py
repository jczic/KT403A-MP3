
from    machine import UART
from    utime   import sleep_ms

class KT403A :

    # ============================================================================
    # ===( Constants )============================================================
    # ============================================================================

    DEVICE_MICRO_SD = 0x02

    EQ_NORMAL       = 0
    EQ_POP          = 1
    EQ_ROCK         = 2
    EQ_JAZZ         = 3
    EQ_CLASSIC      = 4
    EQ_BASS         = 5

    # ============================================================================
    # ===( Constructor )==========================================================
    # ============================================================================

    def __init__(self, uartBus, txPinNum, rxPinNum, device=None) :
        txPinId = "P" + str(txPinNum)
        rxPinId = "P" + str(rxPinNum)
        self._uart = UART( uartBus,
                           baudrate = 9600,
                           pins     = (txPinId, rxPinId, None, None) )
        self.SetDevice(KT403A.DEVICE_MICRO_SD if not device else device)

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
        sleep_ms(200 if cmd == 0x09 else 30)

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
        self._txCmd(0x09, device)

    # ----------------------------------------------------------------------------

    def SetLowPower(self) :
        self._txCmd(0x0A)

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

    def StartLoopingAll(self) :
        self._txCmd(0x11, 1)

    # ----------------------------------------------------------------------------

    def StopLoopingAll(self) :
        self._txCmd(0x11, 0)

    # ----------------------------------------------------------------------------

    def Stop(self) :
        self._txCmd(0x16)

    # ============================================================================
    # ============================================================================
    # ============================================================================
