# geetest
针对geetest的拖动验证码

一个非常不错的geetest验证码教程(https://zhuanlan.zhihu.com/p/22407781), 作者讲的很详细

### geetest_selenium.py
使用selenium进行鼠标的点击和滑动操作
- 默认失败重试3次, 失败后会刷新验证码
- 每次缺口出现的位置不一样, 根据长度大小不同设置3中不同的滑动路径


### geetest_request.py
路径生成函数已经完成, x轴的移动按照由快到慢的过程, passtime非线性累加
然而并没有通过验证, 一直返回失败!!!


### TODO
- 后期加入selenium的隐式等待以缩短时间
- 不适用selenium, 直接提交参数(生成路径后一直被识别为机器人, 还没解决)
