import os
from functools import wraps

from flask import Flask, redirect, render_template, request, session
from pymysql.err import IntegrityError, MySQLError

import db_config


app = Flask(__name__)
app.secret_key = os.getenv("SCORE_APP_SECRET", "score_management_2026")


def alert(message, location=None, back=False):
    safe_message = str(message).replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")
    if back:
        action = "history.back();"
    else:
        action = f"location.href='{location or '/login'}';"
    return f"<script>alert('{safe_message}');{action}</script>"


def require_role(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session.get("role") != role:
                return redirect("/login")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def form_value(name, default=""):
    return request.form.get(name, default).strip()


def validate_score(value):
    try:
        score = float(value)
    except (TypeError, ValueError):
        return None, "分数必须是数字"

    if score < 0 or score > 100:
        return None, "分数范围应为 0 到 100"

    return score, None


@app.errorhandler(MySQLError)
def handle_mysql_error(error):
    print(f"MySQL error: {error}")
    return alert("数据库操作失败，请检查 MySQL 服务、账号密码或数据表状态。", back=True), 500


# ------------------------------ 登录 ------------------------------
@app.route("/")
def index():
    return redirect("/login")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/do_login", methods=["POST"])
def do_login():
    username = form_value("username")
    password = form_value("password")

    if not username or not password:
        return alert("账号和密码不能为空", back=True)

    with db_config.db_cursor() as cur:
        cur.execute("SELECT admin_id, password FROM admin WHERE admin_id=%s", (username,))
        admin = cur.fetchone()
        if admin and admin[1] == password:
            session.clear()
            session["login_user"] = admin[0]
            session["role"] = "admin"
            return alert("管理员登录成功", "/admin/index")

        cur.execute("SELECT student_id, password FROM student WHERE student_id=%s", (username,))
        student = cur.fetchone()
        if student and student[1] == password:
            session.clear()
            session["login_user"] = student[0]
            session["role"] = "student"
            return alert("学生登录成功", "/student/index")

    return alert("账号或密码错误", back=True)


# ------------------------------ 管理员首页 ------------------------------
@app.route("/admin/index")
@require_role("admin")
def admin_index():
    return render_template("admin_index.html")


# ------------------------------ 学生管理 ------------------------------
@app.route("/admin/stu_manage")
@require_role("admin")
def stu_manage():
    with db_config.db_cursor() as cur:
        cur.execute("SELECT student_id, student_name, password FROM student ORDER BY student_id")
        stu_list = [{"student_id": r[0], "student_name": r[1], "password": r[2]} for r in cur.fetchall()]
    return render_template("admin_stu_manage.html", stu_list=stu_list)


@app.route("/admin/add_student", methods=["POST"])
@require_role("admin")
def add_student():
    sid = form_value("student_id")
    name = form_value("student_name")
    pwd = form_value("password") or "123456"

    if not sid or not name:
        return alert("学号和姓名不能为空", back=True)

    try:
        with db_config.db_cursor(commit=True) as cur:
            cur.execute(
                "INSERT INTO student(student_id, student_name, password) VALUES(%s,%s,%s)",
                (sid, name, pwd),
            )
    except IntegrityError:
        return alert("学号已存在", "/admin/stu_manage")

    return alert("添加成功", "/admin/stu_manage")


@app.route("/admin/edit_student")
@require_role("admin")
def edit_student():
    sid = request.args.get("sid", "").strip()
    with db_config.db_cursor() as cur:
        cur.execute("SELECT student_id, student_name, password FROM student WHERE student_id=%s", (sid,))
        one = cur.fetchone()

    if not one:
        return alert("未找到该学生", "/admin/stu_manage")

    stu = {"student_id": one[0], "student_name": one[1], "password": one[2]}
    return render_template("admin_edit_student.html", stu=stu)


@app.route("/admin/save_student", methods=["POST"])
@require_role("admin")
def save_student():
    sid = form_value("student_id")
    name = form_value("student_name")
    pwd = form_value("password")

    if not name or not pwd:
        return alert("姓名和密码不能为空", back=True)

    with db_config.db_cursor(commit=True) as cur:
        cur.execute("UPDATE student SET student_name=%s, password=%s WHERE student_id=%s", (name, pwd, sid))

    return alert("修改成功", "/admin/stu_manage")


@app.route("/admin/del_student")
@require_role("admin")
def del_student():
    sid = request.args.get("sid", "").strip()
    with db_config.db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM score WHERE student_id=%s", (sid,))
        cur.execute("DELETE FROM student WHERE student_id=%s", (sid,))

    return alert("删除成功", "/admin/stu_manage")


# ------------------------------ 科目管理 ------------------------------
@app.route("/admin/course_manage")
@require_role("admin")
def course_manage():
    with db_config.db_cursor() as cur:
        cur.execute("SELECT course_id, course_name, credit FROM course ORDER BY course_id")
        course_list = [{"course_id": r[0], "course_name": r[1], "credit": r[2]} for r in cur.fetchall()]
    return render_template("admin_course_manage.html", course_list=course_list)


@app.route("/admin/add_course", methods=["POST"])
@require_role("admin")
def add_course():
    cid = form_value("course_id")
    cname = form_value("course_name")
    credit = form_value("credit")

    if not cid or not cname or not credit:
        return alert("课程信息不能为空", back=True)

    try:
        with db_config.db_cursor(commit=True) as cur:
            cur.execute(
                "INSERT INTO course(course_id, course_name, credit) VALUES(%s,%s,%s)",
                (cid, cname, credit),
            )
    except IntegrityError:
        return alert("课程编号已存在", "/admin/course_manage")

    return alert("科目添加成功", "/admin/course_manage")


@app.route("/admin/edit_course")
@require_role("admin")
def edit_course():
    cid = request.args.get("cid", "").strip()
    with db_config.db_cursor() as cur:
        cur.execute("SELECT course_id, course_name, credit FROM course WHERE course_id=%s", (cid,))
        one = cur.fetchone()

    if not one:
        return alert("未找到该科目", "/admin/course_manage")

    info = {"course_id": one[0], "course_name": one[1], "credit": one[2]}
    return render_template("admin_edit_course.html", info=info)


@app.route("/admin/save_edit_course", methods=["POST"])
@require_role("admin")
def save_edit_course():
    old_cid = form_value("old_cid")
    new_name = form_value("new_name")
    new_credit = form_value("new_credit")

    if not new_name or not new_credit:
        return alert("课程名称和学分不能为空", back=True)

    with db_config.db_cursor(commit=True) as cur:
        cur.execute("UPDATE course SET course_name=%s, credit=%s WHERE course_id=%s", (new_name, new_credit, old_cid))

    return alert("修改成功", "/admin/course_manage")


@app.route("/admin/del_course")
@require_role("admin")
def del_course():
    cid = request.args.get("cid", "").strip()
    with db_config.db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM score WHERE course_id=%s", (cid,))
        cur.execute("DELETE FROM course WHERE course_id=%s", (cid,))

    return alert("删除成功", "/admin/course_manage")


# ------------------------------ 成绩录入 ------------------------------
@app.route("/admin/add_score")
@require_role("admin")
def add_score():
    with db_config.db_cursor() as cur:
        cur.execute("SELECT course_id, course_name FROM course ORDER BY course_id")
        courses = [{"course_id": r[0], "course_name": r[1]} for r in cur.fetchall()]
    return render_template("admin_add_score.html", courses=courses)


@app.route("/admin/do_add_score", methods=["POST"])
@require_role("admin")
def do_add_score():
    student_id = form_value("student_id")
    course_id = form_value("course_id")
    semester = form_value("semester")
    score, score_error = validate_score(form_value("score"))

    if not student_id or not course_id or not semester:
        return alert("学号、课程和学期不能为空", back=True)
    if score_error:
        return alert(score_error, back=True)

    try:
        with db_config.db_cursor(commit=True) as cur:
            cur.execute("SELECT 1 FROM student WHERE student_id=%s", (student_id,))
            if not cur.fetchone():
                return alert("学号不存在", back=True)

            cur.execute("SELECT 1 FROM course WHERE course_id=%s", (course_id,))
            if not cur.fetchone():
                return alert("课程不存在", back=True)

            cur.execute(
                "INSERT INTO score(student_id, course_id, score, semester) VALUES(%s,%s,%s,%s)",
                (student_id, course_id, score, semester),
            )
    except IntegrityError:
        return alert("该学生该课程已录入成绩，请到成绩修改页面调整", "/admin/score_manage")

    return alert("录入成功", "/admin/add_score")


# ------------------------------ 成绩修改删除 ------------------------------
@app.route("/admin/score_manage")
@require_role("admin")
def score_manage():
    sid = request.args.get("sid", "").strip()

    with db_config.db_cursor() as cur:
        if sid:
            cur.execute(
                """
                SELECT sc.student_id, c.course_name, sc.semester, sc.score, sc.course_id
                FROM score sc
                JOIN course c ON sc.course_id = c.course_id
                WHERE sc.student_id = %s
                ORDER BY sc.semester, sc.course_id
                """,
                (sid,),
            )
        else:
            cur.execute(
                """
                SELECT sc.student_id, c.course_name, sc.semester, sc.score, sc.course_id
                FROM score sc
                JOIN course c ON sc.course_id = c.course_id
                ORDER BY sc.student_id, sc.semester, sc.course_id
                """
            )
        data = [
            {"student_id": r[0], "course_name": r[1], "semester": r[2], "score": r[3], "course_id": r[4]}
            for r in cur.fetchall()
        ]

    return render_template("admin_score_manage.html", score_data=data, sid=sid)


@app.route("/admin/edit_score")
@require_role("admin")
def edit_score():
    sid = request.args.get("sid", "").strip()
    cid = request.args.get("cid", "").strip()
    sem = request.args.get("sem", "").strip()

    with db_config.db_cursor() as cur:
        cur.execute(
            """
            SELECT sc.student_id, c.course_name, sc.semester, sc.score
            FROM score sc
            JOIN course c ON sc.course_id = c.course_id
            WHERE sc.student_id = %s AND sc.course_id = %s AND sc.semester = %s
            """,
            (sid, cid, sem),
        )
        one = cur.fetchone()

    if not one:
        return alert("未找到该成绩记录", "/admin/score_manage")

    info = {"student_id": one[0], "course_name": one[1], "semester": one[2], "score": one[3], "course_id": cid}
    return render_template("admin_edit_score.html", info=info)


@app.route("/admin/do_edit_score", methods=["POST"])
@require_role("admin")
def do_edit_score():
    sid = form_value("sid")
    cid = form_value("cid")
    sem = form_value("sem")
    new_score, score_error = validate_score(form_value("new_score"))

    if score_error:
        return alert(score_error, back=True)

    with db_config.db_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE score SET score=%s WHERE student_id=%s AND course_id=%s AND semester=%s",
            (new_score, sid, cid, sem),
        )

    return alert("修改成功", "/admin/score_manage")


@app.route("/admin/del_score")
@require_role("admin")
def del_score():
    sid = request.args.get("sid", "").strip()
    cid = request.args.get("cid", "").strip()
    sem = request.args.get("sem", "").strip()

    with db_config.db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM score WHERE student_id=%s AND course_id=%s AND semester=%s", (sid, cid, sem))

    return alert("删除成功", "/admin/score_manage")


# ------------------------------ 成绩统计 ------------------------------
@app.route("/admin/score_stat")
@require_role("admin")
def score_stat():
    cid = request.args.get("cid", "").strip()
    sem = request.args.get("sem", "").strip()

    with db_config.db_cursor() as cur:
        cur.execute("SELECT course_id, course_name FROM course ORDER BY course_id")
        course_list = [{"course_id": r[0], "course_name": r[1]} for r in cur.fetchall()]

        sql = """
            SELECT s.student_id, st.student_name, s.semester, c.course_name, s.score
            FROM score s
            JOIN student st ON s.student_id = st.student_id
            JOIN course c ON s.course_id = c.course_id
            WHERE 1 = 1
        """
        params = []
        if cid:
            sql += " AND s.course_id=%s"
            params.append(cid)
        if sem:
            sql += " AND s.semester=%s"
            params.append(sem)
        sql += " ORDER BY s.student_id, s.semester, s.course_id"
        cur.execute(sql, tuple(params))
        res = cur.fetchall()

    stat_list = []
    score_arr = []
    for r in res:
        stat_list.append(
            {"student_id": r[0], "student_name": r[1], "semester": r[2], "course_name": r[3], "score": r[4]}
        )
        score_arr.append(float(r[4]))

    total = len(score_arr)
    max_s = max(score_arr) if total else 0
    min_s = min(score_arr) if total else 0
    avg_s = round(sum(score_arr) / total, 2) if total else 0
    fail = len([x for x in score_arr if x < 60])

    return render_template(
        "admin_score_stat.html",
        course_list=course_list,
        cid=cid,
        sem=sem,
        stat_list=stat_list,
        total_num=total,
        max_score=max_s,
        min_score=min_s,
        avg_score=avg_s,
        fail_num=fail,
    )


# ------------------------------ 成绩打印 ------------------------------
@app.route("/admin/score_print")
@require_role("admin")
def score_print():
    cid = request.args.get("course_id", "").strip()
    term = request.args.get("term", "").strip()

    with db_config.db_cursor() as cur:
        cur.execute("SELECT course_id, course_name FROM course ORDER BY course_id")
        course_data = [{"course_id": r[0], "course_name": r[1]} for r in cur.fetchall()]

        sql = """
            SELECT sc.student_id, st.student_name, sc.semester, co.course_name, sc.score
            FROM score sc
            JOIN student st ON sc.student_id = st.student_id
            JOIN course co ON sc.course_id = co.course_id
            WHERE 1 = 1
        """
        params = []
        if cid:
            sql += " AND sc.course_id=%s"
            params.append(cid)
        if term:
            sql += " AND sc.semester=%s"
            params.append(term)
        sql += " ORDER BY sc.student_id, sc.semester, sc.course_id"
        cur.execute(sql, tuple(params))
        print_list = [
            {"student_id": r[0], "student_name": r[1], "semester": r[2], "course_name": r[3], "score": r[4]}
            for r in cur.fetchall()
        ]

    return render_template(
        "admin_score_print.html",
        course_data=course_data,
        course_id=cid,
        term=term,
        print_list=print_list,
    )


# ------------------------------ 密码管理 ------------------------------
@app.route("/admin/pwd_setting")
@require_role("admin")
def pwd_setting():
    return render_template("admin_pwd_setting.html")


@app.route("/admin/change_admin_pwd", methods=["POST"])
@require_role("admin")
def change_admin_pwd():
    admin_id = session.get("login_user")
    old = form_value("old_pwd")
    new1 = form_value("new_pwd1")
    new2 = form_value("new_pwd2")

    if new1 != new2:
        return alert("两次新密码输入不一致", back=True)

    with db_config.db_cursor(commit=True) as cur:
        cur.execute("SELECT password FROM admin WHERE admin_id=%s", (admin_id,))
        row = cur.fetchone()
        if not row or row[0] != old:
            return alert("原密码错误", back=True)

        cur.execute("UPDATE admin SET password=%s WHERE admin_id=%s", (new1, admin_id))

    return alert("修改成功", "/admin/index")


@app.route("/admin/reset_stu_pwd", methods=["POST"])
@require_role("admin")
def reset_stu_pwd():
    sid = form_value("student_id")
    default_pwd = "123456"

    with db_config.db_cursor(commit=True) as cur:
        cur.execute("SELECT 1 FROM student WHERE student_id=%s", (sid,))
        if not cur.fetchone():
            return alert("学号不存在", back=True)

        cur.execute("UPDATE student SET password=%s WHERE student_id=%s", (default_pwd, sid))

    return alert("已重置为123456", back=True)


# ------------------------------ 学生功能 ------------------------------
@app.route("/student/index")
@require_role("student")
def student_index():
    stu_id = session.get("login_user")

    with db_config.db_cursor() as cur:
        cur.execute("SELECT student_name FROM student WHERE student_id=%s", (stu_id,))
        row = cur.fetchone()

    username = row[0] if row else stu_id
    return render_template("student_index.html", username=username)


@app.route("/student/show_score")
@require_role("student")
def student_show_score():
    stu_id = session.get("login_user")

    with db_config.db_cursor() as cur:
        cur.execute(
            """
            SELECT s.semester, c.course_name, s.score, c.credit
            FROM score s
            JOIN course c ON s.course_id = c.course_id
            WHERE s.student_id = %s
            ORDER BY s.semester, s.course_id
            """,
            (stu_id,),
        )
        score_list = [
            {"semester": r[0], "course_name": r[1], "score": r[2], "credit": r[3]} for r in cur.fetchall()
        ]

    return render_template("student_score.html", score_list=score_list)


@app.route("/student/edit_pwd")
@require_role("student")
def student_edit_pwd():
    return render_template("student_edit_pwd.html")


@app.route("/student/save_stu_pwd", methods=["POST"])
@require_role("student")
def save_stu_pwd():
    stu_id = session.get("login_user")
    old_pwd = form_value("old_pwd")
    new_pwd1 = form_value("new_pwd1")
    new_pwd2 = form_value("new_pwd2")

    if new_pwd1 != new_pwd2:
        return alert("两次新密码输入不一致", back=True)

    with db_config.db_cursor(commit=True) as cur:
        cur.execute("SELECT password FROM student WHERE student_id=%s", (stu_id,))
        row = cur.fetchone()
        if not row or row[0] != old_pwd:
            return alert("原密码错误，请重新输入", back=True)

        cur.execute("UPDATE student SET password=%s WHERE student_id=%s", (new_pwd1, stu_id))

    return alert("密码修改成功，请重新登录", "/logout")


# ------------------------------ 退出 ------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ------------------------------ 启动 ------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True, use_reloader=False)
