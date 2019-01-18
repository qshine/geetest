# geetest
针对geetest的拖动验证码

一个非常不错的geetest验证码教程(https://zhuanlan.zhihu.com/p/22407781), 作者讲的很详细

### geetest_selenium.py
使用selenium进行鼠标的点击和滑动操作
- 默认失败重试3次, 失败后会刷新验证码
- 每次缺口出现的位置不一样, 根据长度大小不同设置3中不同的滑动路径

