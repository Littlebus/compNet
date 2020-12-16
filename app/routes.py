#coding=utf-8
import json

from flask import (abort, flash, jsonify, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.urls import url_parse

import app.evaluator as evaluator
from app import app, db, login
from app.forms import (EvaluateForm, LoginForm, PasswdForm, RecordForm,
                       SignupForm)
from app.models import Evaluation, Record, User
from app.utils import redirect_back

# homepage

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('home.html')


# user

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not check_password_hash(user.password_hash, form.password.data):
            return jsonify({'status': 400, 'message': '无效的用户名或密码'})
        login_user(user)
        return jsonify({'status': 200})
    return render_template('login.html', title='登录', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(
            username      = form.username.data,
            password_hash = generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'status': 200})
    return render_template('signup.html', title='注册', form=form)


# 验证用户名是否被注册的接口
@app.route('/user', methods=['GET'])
def user():
    user = User.query.filter_by(username=request.args.get('username')).first()
    if user is None:
        return jsonify(True)
    return jsonify(False)


@app.route('/passwd', methods=['GET', 'POST'])
@login_required
def passwd():
    form = PasswdForm()
    if form.validate_on_submit():
        current_user.password_hash = generate_password_hash(form.new_password.data)
        db.session.commit()
        flash('修改密码成功', category='info')
        return redirect_back()
    return render_template('passwd.html', title='修改密码', form=form)


# record

@app.route('/record')
@login_required
def record():
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    if q == '':
        pagination = Record.query.order_by(Record.timestamp.desc()) \
            .paginate(page, app.config['PER_PAGE'], False)
    else:
        pagination = Record.query.whooshee_search(q).order_by(Record.timestamp.desc()) \
            .paginate(page, app.config['PER_PAGE'], False)
    return render_template('record.html', title='体检记录', page=page, pagination=pagination)


@app.route('/record/add', methods=['GET', 'POST'])
@login_required
def record_add():
    form = RecordForm()
    if form.validate_on_submit():
        if len(list(request.form.keys())) <= 6:
            flash('没有要提交的体检指标', category='warning')
            return redirect(url_for('record_add'))
        fields = request.form.to_dict()
        if fields is None:
            abort(500)
        record = Record(
            name    = fields['name'],
            user_id = current_user.id,
        )
        del fields['csrf_token']
        del fields['name']
        del fields['submit']
        record.metrics = json.dumps(fields, sort_keys=True)
        db.session.add(record)
        db.session.commit()
        flash('成功添加新记录', category='info')
        return redirect_back()
    return render_template('record_add.html', title='添加记录', form=form)


@app.route('/record/<int:record_id>/delete', methods=['POST'])
@login_required
def record_delete(record_id):
    record = Record.query.get(record_id)
    if current_user != record.creator and not current_user.is_admin():
        flash('没有访问权限', 'warning')
        return redirect_back()
    db.session.delete(record)
    db.session.commit()
    flash('记录删除成功', 'success')
    return redirect_back()


# others

@app.route('/predict/<int:record_id>')
@login_required
def predict(record_id):
    record = Record.query.get(record_id)
    try:
        evaluator.estimate(record)
        db.session.commit()
        flash('预测成功！', 'success')
    except:
        db.session.rollback()
        flash('预测失败！', 'warning')
    return redirect_back()


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    tag = app.config['LABEL']
    B = len(tag)
    q = request.args.get('q', '').strip()
    data_label = 'LABEL'
    data = [0 for _ in range(B)]
    data_list = []
    data_area_base = [[] for _ in range(B + 1)]
    data_area_dir = []

    records = db.session.query(Record).all()
    if q == '':
        for record in records:
            label = record.label
            if not label is None:
                data[label] += 1
                data_list.append((label, label))
    else:
        data_label = q
        for record in records:
            para = record.get_metrics().get(q)
            label = record.label
            if para and not label is None:
                data[label] += 1
                data_list.append((float(para), label))

    total = sum(data)
    pie_data = []
    for i in range(B):
        if total > 0:
            pie_data.append([tag[i], data[i] / total])
        else:
            pie_data.append([tag[i], 0])

    data_list.sort(key=lambda pair: pair[0])
    for k, w in data_list:
        for i in range(B):
            data_area_base[i].append('null')
        data_area_base[w][-1] = k
        data_area_base[B].append(k)

    for i in range(B):
        data_area_dir.append({'name': tag[i], 'data': data_area_base[i]})   
    data_area_dir.append({'name': '总和', 'data': data_area_base[B]}) 

    data_index = [i for i in range(1, total + 1)]

    return render_template('dashboard.html', title='统计数据', pie_data=pie_data,
        data_label=data_label, data_index=data_index, data_area=data_area_dir)


# evaluate
@app.route('/evaluate', methods=['GET', 'POST'])
@login_required
def evaluate():
    form = EvaluateForm()
    if form.validate_on_submit():
        pass
    page = request.args.get('page', 1, type=int)
    pagination = Evaluation.query.order_by(Evaluation.timestamp.desc()) \
        .paginate(page, app.config['PER_PAGE'], False)
    return render_template('evaluate.html', title='冷适应水平评估',
        form=form, page=page, pagination=pagination)
