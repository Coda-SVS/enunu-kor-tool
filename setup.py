# from glob import glob
# from posixpath import basename, splitext
import setuptools

required_packages = [
    "colorlog",
    "tqdm",
    "pyyaml==5.4.1",
    "utaupy==1.18.0",
]

g2p4utau_required_packages = [
    "jamo==0.4.1",
    "regex",
    "g2pk==0.9.3",
]

utaupyk_required_packages = [
    "natsort",
]

# ustx2lab_required_packages = [
# ]

ust2lab4model_required_packages = [
    "colored_traceback",
    "nnsvs",
    "torch==1.11.0",  # pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cu113
]

analysis4vb_required_packages = [
    "matplotlib==3.5.3",
    "mergedeep==1.3.4",
]

total_required_packages = []
total_required_packages += required_packages
total_required_packages += g2p4utau_required_packages
total_required_packages += utaupyk_required_packages
# total_required_packages += ustx2lab_required_packages
total_required_packages += ust2lab4model_required_packages
total_required_packages += analysis4vb_required_packages

total_required_packages = list(set(total_required_packages))

setuptools.setup(
    name="enunu_kor_tool",
    version="0.0.11",
    author="cardroid",
    author_email="carbonsindh@gmail.com",
    description="enunu Korean language support script collection",
    install_requires=required_packages,
    license="MIT",
    packages=setuptools.find_packages(where="src"),
    extras_require={
        "all": total_required_packages,
        "g2p4utau": g2p4utau_required_packages,
        "utaupyk": g2p4utau_required_packages + utaupyk_required_packages,
        "ustx2lab": g2p4utau_required_packages + utaupyk_required_packages,  # + ustx2lab_required_packages,
        "analysis4vb": analysis4vb_required_packages,
        "ust2lab4model": ust2lab4model_required_packages,
    },
    package_dir={"": "src"},
    python_requires=">=3.8",
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "g2pk4utau=enunu_kor_tool.g2pk4utau.g2pk4utau:main",
            "ustx2lab=enunu_kor_tool.entry.ustx2lab:main",
            "lab2ntlab=enunu_kor_tool.entry.lab2ntlab:main",
            "analysis4vb=enunu_kor_tool.analysis4vb.analysis:main",
            "ust2lab4model=enunu_kor_tool.entry.ust2lab4model:main",
        ]
    },
)
