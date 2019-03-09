
from controller.base import BaseHandler

class HelloWorldHandler(BaseHandler):
    URL=r'/HelloWorld'

    def get(self):
        #因为URL是动态地址，所以不能用如下方法来取值
        #name = URL.split('?')[- 1]
        #获取动态地址问号“？”后面的参数值，比如http://localhost:8000/HelloWorld?name=JX_245_1_21
        name=self.get_argument('name')
        #name=JX_254_1_21

        #连接MongoDB数据库，读取name为JX_254_1_21的那条记录的block的值
        #names = list(self.db.page.find({'name':name }))
        names = self.db.page.find_one(dict(name=name))
        blocks=names['blocks']

        self.send_response(blocks)