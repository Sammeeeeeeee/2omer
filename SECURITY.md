# Security Policy - 

> This is valid as V1.0.0
> I will not edit the policy for minor releases, but i will verify it runs safely.

## Vulnerablaties

This is a very simple program, it cannot do much damage. However, as it is a simple python script, if you run a modified version it can cause damage. **No responsibilty taken**, and please ensure to verifiy the hash.

## Supported Versions

These versions have been tested safe to run on current W11 verisons in a sandbox. 

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| 0.x.x   | :x:                |

## Basic properties
  ```
MD5
23c98ad2da70736a9eacc12074ede613 
SHA-1
3d05aece1427b92ff065bc39b97a3b3389fb4133 
SHA-256
1587066a16777214727a0f246d2630820777135c8b929e2dfd06c49072fd94c0 
Vhash
037076655d155515755048z66nz2fz 
Authentihash
5590875f09a500b873ab4d6ef331ea1498211c9131c198c1625506d0f84799f4 
Imphash
bae3d3e8262d7ce7e9ee69cc1b630d3a 
Rich PE header hash
5838a6194acd72edfe34a135e1c1e581 
SSDEEP
786432:F+gX4BMdhwzTQXR5FbPp6FcSS5U/LT2KzVyPVL9jvzVSK1QtIo3ILB:fXGMK4XR3bLSCU/+6yPlhvhSWiIoGB 
TLSH
T1BE873310F2FC1CEDD6B6263591918247DE19F0DE57F3C2DB40A406C35E0BA91AFA9AB4 
File type
Win32 EXE 
executable
windows
win32
pe
peexe

Magic
PE32+ executable (console) x86-64, for MS Windows 
TrID
Win64 Executable (generic) (48.7%)   Win16 NE executable (generic) (23.3%)   OS/2 Executable (generic) (9.3%)   Generic Win/DOS Executable (9.2%)   DOS Executable Generic (9.2%) 
DetectItEasy
PE64   Packer: PyInstaller   Compiler: Microsoft Visual C/C++ (19.36.32826) [C]   Linker: Microsoft Linker (14.36.32826)   Tool: Visual Studio (2022 version 17.6) 
File size
35.53 MB (37254845 bytes)
  ```
## Virustotal score

https://www.virustotal.com/gui/file/1587066a16777214727a0f246d2630820777135c8b929e2dfd06c49072fd94c0/behavior

There are 5 false reports. I belive its due to using QtPy5.

## Reporting a Vulnerability

To report a vunrabiltiy, please open an issue. 
