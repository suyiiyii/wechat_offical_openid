a = 1
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, Request
import aiohttp

appid = 'wx30327296cd76d034'
appsecret = '65b0c394688d34a8a693d6b383341bbd'

DATABASE_URL = "mysql+pymysql://root:mysql_wx@mc.lipids.top:49155/syy"

engine = create_engine(DATABASE_URL)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()
Base.query = db_session.query_property()


class User(Base):
    __tablename__ = "users"

    openid = Column(String(255), primary_key=True, index=True)
    username = Column(String(255), index=True)


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 接受openid参数，返回用户名
@app.get("/userinfo")
async def read_user(request: Request):
    openid = request.query_params.get("openid")
    print(f'查询openid：{openid}')

    user = db_session.query(User).filter(User.openid == openid).first()
    print(user)
    if user == None:
        return "not found openid"
    return user.username


@app.post("/userinfo")
async def create_user(request: Request):
    data = await request.json()
    openid = data.get("openid")
    username = data.get("username")
    print(f'新增openid：{openid}，username：{username}')

    # 判断openid是否存在
    user = db_session.query(User).filter(User.openid == openid).first()
    if user != None:
        return "openid already exists"

    # 新增用户
    user = User(openid=openid, username=username)
    db_session.add(user)
    db_session.commit()
    return "ok"


@app.get("/delete")
async def delete_user(request: Request):
    openid = request.query_params.get("openid")
    print(f'删除openid：{openid}')
    user = db_session.query(User).filter(User.openid == openid).first()
    if user == None:
        return "not found openid"
    db_session.delete(user)
    db_session.commit()
    return "ok"


import json


@app.get("/getOpenid")
async def get_openid(request: Request):
    '''
    接收前端获得的code，向微信服务器发送请求，获取对应的openid
    '''

    code = request.query_params.get("code")
    url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={appsecret}&code={code}&grant_type=authorization_code"
    print(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            try:
                data = await resp.json()
            except aiohttp.client_exceptions.ContentTypeError:
                text = await resp.text()
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    print(f"Failed to decode response text: {text}")
                    raise
            if "openid" in data:
                return data["openid"]
            else:
                return data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
