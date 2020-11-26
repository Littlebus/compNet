#coding=utf-8
import json
from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.urls import url_parse

import app.evaluator as evaluator
from app import app, db, login, search
from app.forms import (ChangePasswordForm, LoginForm, RecordForm,
                       RegistrationForm, UnitForm)
from app.models import Record, Unit, User
from app.utils import redirect_back

# @app.before_request
# def before_request():
#     if current_user.is_authenticated:
#         current_user.last_seen = datetime.utcnow()
#         db.session.commit()


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
            flash('无效的用户名或密码', category='warning')
            return redirect(url_for('login'))
        login_user(user)
        user.last_seen = datetime.utcnow()
        db.session.commit()
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='登录', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username      = form.username.data,
            email         = form.email.data,
            password_hash = generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash('注册成功！', category='info')
        return redirect(url_for('login'))
    return render_template('signup.html', title='注册', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.units.order_by(Unit.timestamp.desc()) \
        .paginate(page, app.config['UNITS_PER_PAGE'], False)
    units = pagination.items
    return render_template('user.html', page=page, pagination=pagination,
        units=units, user=user)


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password_hash = generate_password_hash(form.new_password.data)
        db.session.commit()
        flash('成功修改密码', category='info')
        return redirect_back()
    return render_template('change_password.html', title='修改密码', form=form)


# unit

@app.route('/unit/manage')
@login_required
def unit_manage():
    search.update_index()
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    if q == '':
        pagination = Unit.query.order_by(Unit.timestamp.desc()) \
            .paginate(page, app.config['UNITS_PER_PAGE'], False)
    else:
        pagination = Unit.query.msearch(q, or_=True).order_by(Unit.timestamp.desc()) \
            .paginate(page, app.config['UNITS_PER_PAGE'], False)
    units = pagination.items
    return render_template('manage_unit.html', page=page, pagination=pagination, units=units)


@app.route('/unit/add', methods=['GET', 'POST'])
@login_required
def unit_add():
    form = UnitForm()
    if form.validate_on_submit():
        unit = Unit(
            name      = form.name.data,
            member_id = form.member_id.data,
            age       = form.age.data,
            height    = form.height.data,
            weight    = form.weight.data, 
            user_id   = current_user.id
        )
        db.session.add(unit)
        db.session.commit()
        flash('成功添加新人员', category='info')
        return redirect_back()
    return render_template('add_unit.html', title='添加新人员', form=form)


@app.route('/unit/<int:unit_id>/edit', methods=['GET', 'POST'])
@login_required
def unit_edit(unit_id):
    unit = Unit.query.get(unit_id)
    if current_user != unit.creator and not current_user.is_admin():
        flash('没有访问权限', 'warning')
        return redirect_back()
    form = UnitForm()
    if form.validate_on_submit():
        unit.name = form.name.data
        unit.member_id = form.member_id.data
        unit.age = form.age.data
        unit.height = form.height.data
        unit.weight = form.weight.data
        db.session.commit()
        flash('您的修改已提交', category='info')
        return redirect_back()
    elif request.method == 'GET':  # 这里要区分第一次请求表单的情况
        form.name.data = unit.name
        form.member_id.data = unit.member_id
        form.age.data = unit.age
        form.height.data = unit.height
        form.weight.data = unit.weight
    return render_template('edit_unit.html', title='修改人员信息', unit=unit, form=form)


@app.route('/unit/<int:unit_id>/delete', methods=['POST'])
@login_required
def unit_delete(unit_id):
    unit = Unit.query.get(unit_id)
    if current_user != unit.creator and not current_user.is_admin():
        flash('没有访问权限', 'warning')
        return redirect_back()
    for record in Record.query.filter_by(owner=unit).all():
        db.session.delete(record)
    db.session.delete(unit)
    db.session.commit()
    flash('人员已被删除', 'success')
    return redirect_back()


@app.route('/unit/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def unit(unit_id):
    unit = Unit.query.get(unit_id)
    form = RecordForm()
    form.unit_id.choices = [(unit.id, unit.name)]
    if form.validate_on_submit():
        if len(list(request.form.keys())) <= 3:
            flash('没有要提交的体检指标', category='warning')
            return redirect(url_for('unit', unit_id=unit.id))
        fields = request.form.to_dict()
        if fields:
            del fields['csrf_token']
            del fields['unit_id']
            del fields['submit']
        fields['AGE'] = unit.age
        fields['HEIGHT'] = unit.height
        fields['WEIGHT'] = unit.weight
        record = Record(
            unit_id = unit.id,
            user_id = current_user.id,
            metrics = json.dumps(fields, sort_keys=True)
        )
        db.session.add(record)
        db.session.commit()
        flash('新记录已提交', category='info')
        return redirect(url_for('unit', unit_id=unit.id))
    page = request.args.get('page', 1, type=int)
    pagination = unit.records.order_by(Record.timestamp.desc()) \
        .paginate(page, app.config['UNITS_PER_PAGE'], False)
    records = pagination.items
    return render_template('unit.html', page=page, pagination=pagination,
        records=records, form=form, unit=unit)


# record

@app.route('/record/manage')
@login_required
def record_manage():
    search.update_index()
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    if q == '':
        pagination = Record.query.order_by(Record.timestamp.desc()) \
            .paginate(page, app.config['RECORDS_PER_PAGE'], False)
    else:
        pagination = Record.query.msearch(q, or_=True).order_by(Record.timestamp.desc()) \
            .paginate(page, app.config['RECORDS_PER_PAGE'], False)
    records = pagination.items
    return render_template('manage_record.html', page=page, pagination=pagination, records=records)


@app.route('/record/add', methods=['GET', 'POST'])
@login_required
def record_add():
    form = RecordForm()
    form.unit_id.choices = [(u.id, u.name) for u in Unit.query.all()]
    if form.validate_on_submit():
        if len(list(request.form.keys())) <= 3:
            flash('没有要提交的体检指标', category='warning')
            return redirect(url_for('record_add'))
        fields = request.form.to_dict()
        if fields:
            del fields['csrf_token']
            del fields['unit_id']
            del fields['submit']
        unit = Unit.query.get(form.unit_id.data)
        fields['AGE'] = unit.age
        fields['HEIGHT'] = unit.height
        fields['WEIGHT'] = unit.weight
        record = Record(
            unit_id = form.unit_id.data,
            user_id = current_user.id,
            metrics = json.dumps(fields, sort_keys=True)
        )
        db.session.add(record)
        db.session.commit()
        flash('成功添加新记录', category='info')
        return redirect_back()
    return render_template('add_record.html', title='添加记录', form=form)


@app.route('/record/<int:record_id>/delete', methods=['POST'])
@login_required
def record_delete(record_id):
    record = Record.query.get(record_id)
    if current_user != record.creator and not current_user.is_admin():
        flash('没有访问权限', 'warning')
        return redirect_back()
    db.session.delete(record)
    db.session.commit()
    flash('记录已被删除', 'success')
    return redirect_back()


# others

@app.route('/predict/<int:record_id>')
@login_required
def predict(record_id):
    record = Record.query.get(record_id)
    vrci = record.get_metrics().get('VRCI')
    if vrci:
        vrci = int(vrci)
        if vrci > 12.9:
            record.label = 2
        elif vrci > 9.5:
            record.label = 1
        else:
            record.label = 0

    label, up = evaluator.estimate(record)
    record.label = record.label or label
    record.up = record.up or up
    db.session.commit()
    flash('预测成功！', 'success')
    print(record.label, record.up)
    return redirect_back()


@app.route('/dashboards', methods=['GET', 'POST'])
@login_required
def dashboards():
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

    return render_template('dashboards.html', pie_data=pie_data, data_label=data_label, \
        data_index=data_index, data_area=data_area_dir)
