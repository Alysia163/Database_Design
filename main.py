# main.py
from score_management_web.db_config import get_db_connection
import csv

# ===================== 原有基础函数不变 =====================
def check_user(account, pwd):
    conn = get_db_connection()
    if not conn:
        return "error", None, None
    cursor = conn.cursor()
    cursor.execute("SELECT admin_id,password FROM admin WHERE admin_id=%s", (account,))
    admin = cursor.fetchone()
    if admin:
        if admin[1] == pwd:
            cursor.close()
            conn.close()
            return "admin", admin[0], admin[1]
        else:
            cursor.close()
            conn.close()
            return "error", None, None
    cursor.execute("SELECT student_name,password FROM student WHERE student_id=%s", (account,))
    student = cursor.fetchone()
    if student:
        if student[1] == pwd:
            cursor.close()
            conn.close()
            return "student", student[0], student[1]
        else:
            cursor.close()
            conn.close()
            return "error", None, None
    cursor.close()
    conn.close()
    return "error", None, None

def modify_password(role, account):
    print("\n初始密码请先修改再使用")
    old_pwd = input("原密码：")
    if old_pwd in ("exit", "q"):
        return False
    new_pwd = input("新密码：")
    if new_pwd in ("exit", "q"):
        return False
    confirm_pwd = input("确认新密码：")
    if confirm_pwd in ("exit", "q"):
        return False
    if new_pwd != confirm_pwd:
        print("两次密码不一致")
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    if role == "admin":
        cursor.execute("UPDATE admin SET password=%s WHERE admin_id=%s", (new_pwd, account))
    else:
        cursor.execute("UPDATE student SET password=%s WHERE student_id=%s", (new_pwd, account))
    conn.commit()
    print("密码修改成功，请重新登录")
    cursor.close()
    conn.close()
    return True

def student_change_password(student_id):
    print("\n===== 修改个人密码 =====")
    old_pwd = input("当前密码：")
    if old_pwd in ("exit", "q"):
        return
    new_pwd = input("新密码：")
    if new_pwd in ("exit", "q"):
        return
    confirm_pwd = input("确认新密码：")
    if confirm_pwd in ("exit", "q"):
        return
    if new_pwd != confirm_pwd:
        print("两次密码不一致")
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM student WHERE student_id=%s", (student_id,))
    real_pwd = cursor.fetchone()[0]
    if real_pwd != old_pwd:
        print("原密码错误")
        cursor.close()
        conn.close()
        return
    cursor.execute("UPDATE student SET password=%s WHERE student_id=%s", (new_pwd, student_id))
    conn.commit()
    print("密码修改成功")
    cursor.close()
    conn.close()

def admin_reset_student_password():
    print("\n===== 重置学生密码 =====")
    sid = input("输入学生学号：")
    if sid in ("exit", "q"):
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM student WHERE student_id=%s", (sid,))
    if not cur.fetchone():
        print("学生不存在")
        cur.close()
        conn.close()
        return
    cur.execute("UPDATE student SET password='123456' WHERE student_id=%s", (sid,))
    conn.commit()
    print("密码已重置为123456")
    cur.close()
    conn.close()

def admin_change_self_password(admin_id):
    print("\n===== 修改管理员密码 =====")
    old_pwd = input("当前密码：")
    if old_pwd in ("exit", "q"):
        return
    new_pwd = input("新密码：")
    if new_pwd in ("exit", "q"):
        return
    confirm_pwd = input("确认新密码：")
    if confirm_pwd in ("exit", "q"):
        return
    if new_pwd != confirm_pwd:
        print("两次密码不一致")
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT password FROM admin WHERE admin_id=%s", (admin_id,))
    real_pwd = cur.fetchone()[0]
    if real_pwd != old_pwd:
        print("原密码错误")
        cur.close()
        conn.close()
        return
    cur.execute("UPDATE admin SET password=%s WHERE admin_id=%s", (new_pwd, admin_id))
    conn.commit()
    print("管理员密码修改成功")
    cur.close()
    conn.close()

# 学生管理
def admin_add_student():
    print("\n===== 添加学生 =====")
    sid = input("学生学号：")
    if sid in ("exit", "q"):
        return
    sname = input("学生姓名：")
    if sname in ("exit", "q"):
        return
    depart = input("所属院系：")
    major = input("所属专业：")
    cls = input("所属班级：")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM student WHERE student_id=%s", (sid,))
    if cur.fetchone():
        print("学号已存在")
    else:
        cur.execute("INSERT INTO student(student_id,student_name,password,department,major,class) VALUES(%s,%s,'123456',%s,%s,%s)", (sid, sname, depart, major, cls))
        conn.commit()
        print("添加成功，初始密码123456")
    cur.close()
    conn.close()

def admin_del_student():
    print("\n===== 删除学生 =====")
    sid = input("学生学号：")
    if sid in ("exit", "q"):
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM student WHERE student_id=%s", (sid,))
    if not cur.fetchone():
        print("学生不存在")
        cur.close()
        conn.close()
        return
    cur.execute("DELETE FROM score WHERE student_id=%s", (sid,))
    cur.execute("DELETE FROM student WHERE student_id=%s", (sid,))
    conn.commit()
    print("学生及对应成绩已删除")
    cur.close()
    conn.close()

def admin_show_all_student():
    print("\n===== 全部学生列表 =====")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT student_id,student_name,department,major,class FROM student")
    data = cur.fetchall()
    if not data:
        print("暂无学生数据")
    else:
        print("学号\t姓名\t院系\t专业\t班级")
        for i in data:
            print(f"{i[0]}\t{i[1]}\t{i[2]}\t{i[3]}\t{i[4]}")
    cur.close()
    conn.close()

# 课程管理
def admin_add_course():
    print("\n===== 添加考试科目 =====")
    cid = input("课程编号：")
    if cid in ("exit", "q"):
        return
    cname = input("课程名称：")
    if cname in ("exit", "q"):
        return
    credit = input("课程学分：")
    pass_score = input("及格分数线：")
    if credit in ("exit", "q") or pass_score in ("exit", "q"):
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM course WHERE course_id=%s", (cid,))
    if cur.fetchone():
        print("课程编号已存在")
    else:
        cur.execute("INSERT INTO course(course_id,course_name,credit,pass_line) VALUES(%s,%s,%s,%s)", (cid, cname, credit, pass_score))
        conn.commit()
        print("考试科目添加成功")
    cur.close()
    conn.close()

def admin_del_course():
    print("\n===== 删除考试科目 =====")
    cid = input("课程编号：")
    if cid in ("exit", "q"):
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM course WHERE course_id=%s", (cid,))
    if not cur.fetchone():
        print("课程不存在")
        cur.close()
        conn.close()
        return
    cur.execute("DELETE FROM score WHERE course_id=%s", (cid,))
    cur.execute("DELETE FROM course WHERE course_id=%s", (cid,))
    conn.commit()
    print("科目及对应成绩已删除")
    cur.close()
    conn.close()

def admin_show_all_course():
    print("\n===== 全部考试科目 =====")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT course_id,course_name,credit,pass_line FROM course")
    data = cur.fetchall()
    if not data:
        print("暂无科目数据")
    else:
        print("编号\t科目名\t学分\t及格线")
        for i in data:
            print(f"{i[0]}\t{i[1]}\t{i[2]}\t{i[3]}")
    cur.close()
    conn.close()

# 成绩基础操作
def admin_add_score():
    print("\n===== 手动录入成绩 =====")
    sid = input("学生学号：")
    if sid in ("exit", "q"):
        return
    cid = input("科目编号：")
    if cid in ("exit", "q"):
        return
    sco = input("考试分数：")
    if sco in ("exit", "q"):
        return
    term = input("所属学期：")
    if term in ("exit", "q"):
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM student WHERE student_id=%s", (sid,))
    if not cur.fetchone():
        print("学生不存在")
        cur.close()
        conn.close()
        return
    cur.execute("SELECT 1 FROM course WHERE course_id=%s", (cid,))
    if not cur.fetchone():
        print("考试科目不存在")
        cur.close()
        conn.close()
        return
    cur.execute("SELECT 1 FROM score WHERE student_id=%s AND course_id=%s", (sid, cid))
    if cur.fetchone():
        print("该生此科目成绩已存在")
        cur.close()
        conn.close()
        return
    try:
        s = int(sco)
    except:
        print("分数必须为数字")
        cur.close()
        conn.close()
        return
    if s < 0 or s > 100:
        print("分数范围0-100")
        cur.close()
        conn.close()
        return
    cur.execute("INSERT INTO score VALUES(%s,%s,%s,%s)", (sid, cid, sco, term))
    conn.commit()
    print("成绩录入成功")
    cur.close()
    conn.close()

def admin_update_score():
    print("\n===== 修改成绩信息 =====")
    sid = input("学生学号：")
    if sid in ("exit", "q"):
        return
    cid = input("科目编号：")
    if cid in ("exit", "q"):
        return
    newsco = input("新分数：")
    if newsco in ("exit", "q"):
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM student WHERE student_id=%s", (sid,))
    if not cur.fetchone():
        print("学生不存在")
        cur.close()
        conn.close()
        return
    cur.execute("SELECT 1 FROM course WHERE course_id=%s", (cid,))
    if not cur.fetchone():
        print("科目不存在")
        cur.close()
        conn.close()
        return
    try:
        ns = int(newsco)
    except:
        print("分数必须为数字")
        cur.close()
        conn.close()
        return
    if ns < 0 or ns > 100:
        print("分数范围0-100")
        cur.close()
        conn.close()
        return
    cur.execute("UPDATE score SET score=%s WHERE student_id=%s AND course_id=%s", (newsco, sid, cid))
    conn.commit()
    print("成绩修改完成")
    cur.close()
    conn.close()

def admin_del_single_score():
    print("\n===== 删除单科成绩 =====")
    sid = input("学生学号：")
    if sid in ("exit", "q"):
        return
    cid = input("科目编号：")
    if cid in ("exit", "q"):
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM score WHERE student_id=%s AND course_id=%s", (sid, cid))
    if not cur.fetchone():
        print("暂无该条成绩记录")
        cur.close()
        conn.close()
        return
    cur.execute("DELETE FROM score WHERE student_id=%s AND course_id=%s", (sid, cid))
    conn.commit()
    print("单科成绩删除成功")
    cur.close()
    conn.close()

def admin_query_student_score():
    print("\n===== 按学号查询成绩 =====")
    sid = input("学生学号：")
    if sid in ("exit", "q"):
        return
    term = input("指定学期(回车查全部)：")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM student WHERE student_id=%s", (sid,))
    if not cur.fetchone():
        print("学生不存在")
        cur.close()
        conn.close()
        return
    if term.strip() == "":
        sql = "SELECT c.course_name,s.score,c.pass_line,s.semester FROM score s JOIN course c ON s.course_id=c.course_id WHERE s.student_id=%s"
        cur.execute(sql, (sid,))
    else:
        sql = "SELECT c.course_name,s.score,c.pass_line,s.semester FROM score s JOIN course c ON s.course_id=c.course_id WHERE s.student_id=%s AND s.semester=%s"
        cur.execute(sql, (sid, term))
    data = cur.fetchall()
    if not data:
        print("无对应成绩数据")
    else:
        print("科目名称\t分数\t及格线\t学期")
        for item in data:
            print(f"{item[0]}\t{item[1]}\t{item[2]}\t{item[3]}")
    cur.close()
    conn.close()

def student_score_system(sid, sname):
    while True:
        print(f"\n欢迎 {sname}")
        print("1.查看学期各科成绩  2.修改个人密码  0.退出登录")
        opt = input("选择：")
        if opt == "1":
            conn = get_db_connection()
            cur = conn.cursor()
            sql = "SELECT c.course_name,s.score,c.credit,s.semester FROM score s JOIN course c ON s.course_id=c.course_id WHERE s.student_id=%s ORDER BY semester"
            cur.execute(sql, (sid,))
            res = cur.fetchall()
            print("\n个人学期成绩表")
            for i in res:
                print(f"学期{i[3]} | {i[0]} | 分数：{i[1]} | 学分：{i[2]}")
            cur.close()
            conn.close()
        elif opt == "2":
            student_change_password(sid)
        elif opt == "0":
            break
        else:
            print("无效选择")

# ===================== ① 系统设置：参数+权限+改密 =====================
def system_setting_menu(admin_id):
    while True:
        print("\n===== 系统参数设置 =====")
        print("1.修改管理员登录密码")
        print("2.设置等级分值标准")
        print("3.用户权限管理")
        print("0.返回上级菜单")
        opt = input("请选择：")
        if opt == "1":
            admin_change_self_password(admin_id)
        elif opt == "2":
            set_score_grade()
        elif opt == "3":
            authority_manage()
        elif opt == "0":
            break
        else:
            print("输入无效")

# 设置优良中差等级分值
def set_score_grade():
    print("\n===== 设置成绩等级划分分值 =====")
    excellent = input("优秀最低分：")
    good = input("良好最低分：")
    medium = input("中等最低分：")
    pass_line = input("及格最低分：")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE score_grade")
    cur.execute("INSERT INTO score_grade(excellent,good,medium,pass_score) VALUES(%s,%s,%s,%s)",(excellent,good,medium,pass_line))
    conn.commit()
    print("成绩等级分值设置保存成功")
    cur.close()
    conn.close()

# 简单权限管理
def authority_manage():
    print("\n===== 用户权限设置 =====")
    print("1.开放学生仅查询权限")
    print("2.关闭学生自主改密权限")
    print("3.恢复全部学生权限")
    print("0.退出")
    op = input("选择：")
    conn = get_db_connection()
    cur = conn.cursor()
    if op == "1":
        cur.execute("UPDATE sys_auth SET stu_query=1,stu_modify_pwd=0")
        conn.commit()
        print("已设置学生仅能查成绩，不能改密码")
    elif op == "2":
        cur.execute("UPDATE sys_auth SET stu_modify_pwd=0")
        conn.commit()
        print("已关闭学生改密权限")
    elif op == "3":
        cur.execute("UPDATE sys_auth SET stu_query=1,stu_modify_pwd=1")
        conn.commit()
        print("已恢复学生全部权限")
    cur.close()
    conn.close()

# ===================== ③ 成绩批量导入（CSV表格导入） =====================
def import_score_from_csv():
    print("\n===== 从外部表格导入成绩 =====")
    path = input("请输入csv文件完整路径：")
    try:
        with open(path,"r",encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            conn = get_db_connection()
            cur = conn.cursor()
            cnt = 0
            for row in reader:
                if len(row)!=4:
                    continue
                sid,cid,score,term = row
                cur.execute("SELECT 1 FROM student WHERE student_id=%s",(sid,))
                cur.execute("SELECT 1 FROM course WHERE course_id=%s",(cid,))
                if cur.fetchone() and cur.fetchone():
                    cur.execute("SELECT 1 FROM score WHERE student_id=%s AND course_id=%s",(sid,cid))
                    if not cur.fetchone():
                        cur.execute("INSERT INTO score VALUES(%s,%s,%s,%s)",(sid,cid,score,term))
                        cnt += 1
            conn.commit()
            print(f"成功导入 {cnt} 条学生成绩数据")
            cur.close()
            conn.close()
    except Exception as e:
        print(f"导入失败：{str(e)}")

# ===================== ⑤ 院系/专业/班级分类成绩统计 =====================
def class_depart_score_stat():
    print("\n===== 分类成绩统计 =====")
    print("1.按院系统计 2.按专业统计 3.按班级统计 0.退出")
    cho = input("选择：")
    conn = get_db_connection()
    cur = conn.cursor()
    if cho == "1":
        depart = input("输入查询院系名称：")
        sql = """
        SELECT AVG(s.score),MAX(s.score),MIN(s.score),
        SUM(CASE WHEN s.score<c.pass_line THEN 1 ELSE 0 END) fail_num
        FROM score s
        JOIN student st ON s.student_id=st.student_id
        JOIN course c ON s.course_id=c.course_id
        WHERE st.department=%s
        """
        cur.execute(sql,(depart,))
        avg_sco,max_sco,min_sco,fail = cur.fetchone()
        print(f"院系平均分：{round(avg_sco,2)} 最高分：{max_sco} 最低分：{min_sco} 不及格人数：{fail}")
    elif cho == "2":
        major = input("输入查询专业名称：")
        sql = """
        SELECT AVG(s.score),MAX(s.score),MIN(s.score),
        SUM(CASE WHEN s.score<c.pass_line THEN 1 ELSE 0 END) fail_num
        FROM score s
        JOIN student st ON s.student_id=st.student_id
        JOIN course c ON s.course_id=c.course_id
        WHERE st.major=%s
        """
        cur.execute(sql,(major,))
        avg_sco,max_sco,min_sco,fail = cur.fetchone()
        print(f"专业平均分：{round(avg_sco,2)} 最高分：{max_sco} 最低分：{min_sco} 不及格人数：{fail}")
    elif cho == "3":
        cls = input("输入查询班级：")
        sql = """
        SELECT AVG(s.score),MAX(s.score),MIN(s.score),
        SUM(CASE WHEN s.score<c.pass_line THEN 1 ELSE 0 END) fail_num
        FROM score s
        JOIN student st ON s.student_id=st.student_id
        JOIN course c ON s.course_id=c.course_id
        WHERE st.class=%s
        """
        cur.execute(sql,(cls,))
        avg_sco,max_sco,min_sco,fail = cur.fetchone()
        print(f"班级平均分：{round(avg_sco,2)} 最高分：{max_sco} 最低分：{min_sco} 不及格人数：{fail}")
    cur.close()
    conn.close()

# ===================== ⑥ 成绩分类打印（控制台模拟打印） =====================
def print_score_data():
    print("\n===== 成绩分类打印 =====")
    print("1.打印全院系成绩 2.打印专业成绩 3.打印班级成绩 4.打印单人成绩 0.退出")
    p_opt = input("选择打印类型：")
    conn = get_db_connection()
    cur = conn.cursor()
    if p_opt == "1":
        d = input("输入院系名称：")
        sql = """
        SELECT st.student_id,st.student_name,c.course_name,s.score,s.semester
        FROM score s
        JOIN student st ON s.student_id=st.student_id
        JOIN course c ON s.course_id=c.course_id
        WHERE st.department=%s ORDER BY st.student_id
        """
        cur.execute(sql,(d,))
        data = cur.fetchall()
        print("\n==========院系成绩打印报表==========")
        for item in data:
            print(f"学号:{item[0]} 姓名:{item[1]} 科目:{item[2]} 分数:{item[3]} 学期:{item[4]}")
    elif p_opt == "2":
        m = input("输入专业名称：")
        sql = """
        SELECT st.student_id,st.student_name,c.course_name,s.score,s.semester
        FROM score s
        JOIN student st ON s.student_id=st.student_id
        JOIN course c ON s.course_id=c.course_id
        WHERE st.major=%s ORDER BY st.class
        """
        cur.execute(sql,(m,))
        data = cur.fetchall()
        print("\n==========专业成绩打印报表==========")
        for item in data:
            print(f"学号:{item[0]} 姓名:{item[1]} 科目:{item[2]} 分数:{item[3]} 学期:{item[4]}")
    elif p_opt == "3":
        cl = input("输入班级：")
        sql = """
        SELECT st.student_id,st.student_name,c.course_name,s.score,s.semester
        FROM score s
        JOIN student st ON s.student_id=st.student_id
        JOIN course c ON s.course_id=c.course_id
        WHERE st.class=%s
        """
        cur.execute(sql,(cl,))
        data = cur.fetchall()
        print("\n==========班级成绩打印报表==========")
        for item in data:
            print(f"学号:{item[0]} 姓名:{item[1]} 科目:{item[2]} 分数:{item[3]} 学期:{item[4]}")
    elif p_opt == "4":
        sid = input("输入学生学号：")
        sql = """
        SELECT c.course_name,s.score,s.semester
        FROM score s JOIN course c ON s.course_id=c.course_id
        WHERE s.student_id=%s
        """
        cur.execute(sql,(sid,))
        data = cur.fetchall()
        print("\n==========个人成绩单==========")
        for item in data:
            print(f"学期{item[2]} {item[0]}：{item[1]}分")
    cur.close()
    conn.close()

# ===================== 管理员总菜单（整合全部需求） =====================
def admin_menu(admin_id):
    while True:
        print("\n========== 成绩管理系统-管理员后台 ==========")
        print("【1系统设置】【2学生管理】【3考试科目管理】")
        print("【4成绩手动录入】【5批量导入成绩】【6成绩信息修改删除】")
        print("【7分类成绩统计】【8成绩分类打印】【9学生成绩查询】")
        print("0.退出管理员后台")
        main_opt = input("请选择功能序号：")
        if main_opt == "1":
            system_setting_menu(admin_id)
        elif main_opt == "2":
            print("\n1新增学生 2删除学生 3查看全部学生")
            s_op = input("选择：")
            if s_op=="1":admin_add_student()
            elif s_op=="2":admin_del_student()
            elif s_op=="3":admin_show_all_student()
        elif main_opt == "3":
            print("\n1新增考试科目 2删除科目 3查看全部科目")
            c_op = input("选择：")
            if c_op=="1":admin_add_course()
            elif c_op=="2":admin_del_course()
            elif c_op=="3":admin_show_all_course()
        elif main_opt == "4":
            admin_add_score()
        elif main_opt == "5":
            import_score_from_csv()
        elif main_opt == "6":
            print("1修改成绩 2删除单科成绩")
            up_op = input("选择：")
            if up_op=="1":admin_update_score()
            elif up_op=="2":admin_del_single_score()
        elif main_opt == "7":
            class_depart_score_stat()
        elif main_opt == "8":
            print_score_data()
        elif main_opt == "9":
            admin_query_student_score()
        elif main_opt == "0":
            print("退出管理员后台成功")
            break
        else:
            print("功能序号输入错误")

# 登录入口
def login_system():
    print("\n===== 成绩管理系统登录 =====")
    user = input("账号：")
    pwd = input("密码：")
    res = check_user(user, pwd)
    if res[0] == "error":
        print("账号或密码错误")
        return
    role, name, oldpwd = res
    if oldpwd == "123456":
        modify_password(role, user)
        return
    if role == "admin":
        admin_menu(user)
    else:
        student_score_system(user, name)

# 主程序
if __name__ == "__main__":
    while True:
        print("\n========== 成绩管理系统主界面 ==========")
        print("1.用户登录进入系统")
        print("0.关闭退出系统")
        choose = input("请选择：")
        if choose == "1":
            login_system()
        elif choose == "0":
            print("系统已安全退出")
            break
        else:
            print("无效输入，请重新选择")