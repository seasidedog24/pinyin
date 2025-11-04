# Pinyin

**文件目录以及格式**

`corpus` ：语料库文件目录

`data`：测试输入、测试输出、标准输出文件目录

`src`：源代码文件目录

`res`：模型数据文件目录

`src/alphabet`：拼音汉字表目录

## 使用二元模型

```bash
python main.py [-h] [-a ALPHA]
```

参数说明：

+ `-a`：alpha 参数，默认为`1e-7`


## 目录结构

```
.
├── corpus
├── data
│   ├── answer.txt
│   ├── input.txt
│   └── output.txt
├── main.py
├── readme.md
├── report.md
├── requirements.txt
├── res
└── src
    ├── alphabet
    │   ├── 拼音汉字表.txt
    │   └── 一二级汉字表.txt
    ├── const.py
    ├── judge.py
    ├── predict.py
    └── train.py
```