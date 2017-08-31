
from kt403A import KT403A

print("-----------------")
print(" Test KT403A MP3 ")
print("-----------------")

mp3 = KT403A(1, 3, 4)
mp3.SetVolume(70)
mp3.StartLoopingAll()
