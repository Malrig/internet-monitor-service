import docker


class MongoMocked:
    def __init__(self):
        self.client = docker.from_env()
        self.container = self.client.containers.run("mongo:4", detach=True,
                                                    ports={"27017/tcp": 27017}, remove=True)

    def clean_mongo(self):
        self.container.exec_run("mongo --eval 'db.dropDatabase();'")

    def tear_down_mongo(self):
        self.container.stop()
