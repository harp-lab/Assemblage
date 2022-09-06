from assemblage.data.db import DBManager
import re
db_man = DBManager("mysql+pymysql://root:assemblage@172.18.0.2:3306/assemblage?charset=utf8mb4")
status = []
for opt in [1,6,7,8]:
    for c_status in [2,4,5,6,10]:
        fail_statuses = db_man.find_status_by_status_code(clone_status=3, build_status=c_status, build_opt_id=opt, limit=-1)
        for fail_status in fail_statuses:
            if re.sub(' +', ' ', fail_status.clone_msg ) != " " and fail_status.clone_msg!="":
                status.append(
                    fail_status.build_msg,
                )


with open("builderr.txt","a") as f:
    for x in status:
        f.write(x.strip())
