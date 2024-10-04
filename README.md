# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/Carrera-Dev-Consulting/zombie_dice/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------ | -------: | -------: | ------: | --------: |
| zombie\_dice/\_\_init\_\_.py        |        1 |        0 |    100% |           |
| zombie\_dice/\_\_main\_\_.py        |       12 |       12 |      0% |      1-24 |
| zombie\_dice/cli.py                 |       12 |       12 |      0% |      6-37 |
| zombie\_dice/engine.py              |       67 |       20 |     70% |93-94, 97-100, 103-109, 113, 116-126 |
| zombie\_dice/models/\_\_init\_\_.py |        0 |        0 |    100% |           |
| zombie\_dice/models/bag.py          |       18 |        6 |     67% | 14, 17-22 |
| zombie\_dice/models/dice.py         |       26 |        0 |    100% |           |
|                           **TOTAL** |  **136** |   **50** | **63%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/Carrera-Dev-Consulting/zombie_dice/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/Carrera-Dev-Consulting/zombie_dice/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Carrera-Dev-Consulting/zombie_dice/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/Carrera-Dev-Consulting/zombie_dice/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2FCarrera-Dev-Consulting%2Fzombie_dice%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/Carrera-Dev-Consulting/zombie_dice/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.