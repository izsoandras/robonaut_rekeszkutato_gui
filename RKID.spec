# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['RKIgui.py'],
             pathex=['C:\\Users\\Tarsoly\\Programming\\Python\\robonaut_rekeszkutato_gui'],
             binaries=[],
             datas=[('./assets', 'assets/'), ('./settings', 'settings/')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='RKID',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='assets\\icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='RKID')
