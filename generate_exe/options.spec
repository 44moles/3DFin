# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ["../code/3DFin.py"],
    pathex=["../code/"],
    binaries=[],
    datas=[
        ("../files/stripe.png", "."),
        ("../files/original_cloud.png", "."),
        ("../files/normalized_cloud.png", "."),
        ("../files/info_icon.png", "."),
        ("../files/section_details.png", "."),
        ("../files/sectors.png", "."),
        ("../files/documentation.pdf", "."),
        ("../files/3dfin_logo.png", "."),
        ("../files/icon_window.ico", "."),
        ("../files/warning_img_1.png", "."),
        ("../files/carlos_pic_1.jpg", "."),
        ("../files/celestino_pic_1.jpg", "."),
        ("../files/diego_pic_1.jpg", "."),
        ("../files/cris_pic_1.jpg", "."),
        ("../files/stefan_pic_1.jpg", "."),
        ("../files/tadas_pic_1.jpg", "."),
        ("../files/covadonga_pic_1.jpg", "."),
        ("../files/uniovi_logo_1.png", "."),
        ("../files/nerc_logo_1.png", "."),
        ("../files/spain_logo_1.png", "."),
        ("../files/csic_logo_1.png", "."),
        ("../files/swansea_logo_1.png", "."),
        ("../files/License.txt", "."),
    ],
    hiddenimports=[
        "jakteristics.utils",
        "xlsxwriter",
        "laszip",
        "lazrs",
        "sklearn.metrics._pairwise_distances_reduction._datasets_pair",
        "sklearn.metrics._pairwise_distances_reduction._base",
        "sklearn.metrics._pairwise_distances_reduction._middle_term_computer",
        " xlsxwriter"
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="3DFin",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=["icon_window.ico"],
)
