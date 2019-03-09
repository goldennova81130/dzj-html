#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 在 controller.views 包实现页面响应类，生成前端页面，modules 为重用网页片段的渲染类

from . import modules, home, user, task

handlers = [home.HomeHandler,
            user.LoginHandler, user.RegisterHandler,
            user.UsersHandler, user.UserRolesHandler, user.UsersDataHandler,user.UsersProfileHandler,
            task.ChooseCharProofHandler, task.ChooseCharReviewHandler, task.MyTasksHandler,
            task.ChooseCutProofHandler, task.ChooseCutReviewHandler,
            task.CharProofDetailHandler, task.CutProofDetailHandler,
            task.CutStatusHandler, task.TextStatusHandler]

modules = {'CommonLeft': modules.CommonLeft, 'CommonHead': modules.CommonHead}
