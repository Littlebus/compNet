#coding=utf-8
import json
import pandas as pd
from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.urls import url_parse

import app.evaluator as evaluator
from app import app, db, login, search
from app.email import send_password_reset_email
from app.forms import (ChangePasswordForm, EvaluateForm, LoginForm, RecordForm, RegistrationForm,
                       ResetPasswordForm, ResetPasswordRequestForm, UnitForm)
from app.models import Evaluation, Record, Unit, User
from app.utils import addtodict3, redirect_back


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


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
        login_user(user, remember=form.remember_me.data)
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


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('已发送重置密码邮件', category='info')
        else:
            flash('电子邮箱未注册', category='warning')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='重置密码', form=form)


@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_jwt_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash('您的密码已重置', category='info')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


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
    page = request.args.get('page', 1, type=int)
    pagination = Unit.query.order_by(Unit.timestamp.desc()) \
        .paginate(page, app.config['UNITS_PER_PAGE_ADD'], False)
    units = pagination.items
    return render_template('add_unit.html', title='添加新人员', form=form,
                           units=units, pagination=pagination)


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
            flash("没有要提交的体检指标", category="warning")
            return redirect(url_for('unit', unit_id=unit.id))
        fields = request.form.to_dict()
        if fields:
            del fields['csrf_token']
            del fields['unit_id']
            del fields['submit']
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
    if unit.creator == current_user or current_user.is_admin():
        return render_template('unit.html', page=page, pagination=pagination,
            records=records, form=form, unit=unit)
    else:
        return render_template('unit.html', page=page, pagination=pagination,
            records=records, unit=unit)


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
            flash("没有要提交的体检指标", category="warning")
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
    page = request.args.get('page', 1, type=int)
    pagination = Record.query.order_by(Record.timestamp.desc()) \
        .paginate(page, app.config['RECORDS_PER_PAGE_ADD'], False)
    records = pagination.items
    return render_template('add_record.html', title='添加记录', form=form,
                           records=records, pagination=pagination)


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

@app.route('/quick_evaluation', methods=['GET', 'POST'])
@login_required
def quick_evaluation():
    page = request.args.get('page', 1, type=int)
    pagination = Evaluation.query.order_by(Evaluation.timestamp.desc()).paginate(
        page, app.config['EVALUATIONS_PER_PAGE_ADD'], False)
    evaluations = pagination.items
    return render_template('quick_evaluation.html', title='Quick Evaluate', evaluations=evaluations, pagination=pagination, page=page)

@app.route('/add_evaluation', methods=['GET', 'POST'])
@login_required
def add_evaluation():
    form = EvaluateForm()
    form.record_id.choices = [(r.id, r.metrics) for r in Record.query.all()] 
    if form.validate_on_submit():
        metrics_temp = Record.query.get(form.record_id.data).metrics
        # load model
        model = evaluator.load_model()
        field_names = model.columns.values.tolist()
        dic_input = json.loads(metrics_temp)
        dic_test = {}
        for word in field_names:
            if word in dic_input:
                dic_test[word] = dic_input[word]
        result = evaluator.estimate(model, dic_test)
        evaluation = Evaluation(metrics=metrics_temp, label=result)
        print(evaluation)
        db.session.add(evaluation)
        db.session.commit()
        flash('您的快速诊断记录已经被提交', category='success')
        return redirect_back()
    return render_template('add_evaluation.html', title='Add Evaluate', form=form)

@app.route('/delete_evaluation/<int:evaluation_id>', methods=['POST'])
@login_required
def delete_evaluation(evaluation_id):
    evaluation = Evaluation.query.get(evaluation_id)
    if(current_user.is_admin() == False):
        flash('没有访问权限', 'warning')
        return redirect_back()
    db.session.delete(evaluation)
    db.session.commit()
    flash('快速诊断记录已经被删除', 'success')
    return redirect_back()

@app.route('/dashboards', methods=['GET', 'POST'])
@login_required
def dashboards():
    # 下面这一行完成的是分类统计，按照Evaluation.gender，统计两个性别的人数
    # evaluations = db.session.query(Evaluation.gender, func.sum(1)).group_by(Evaluation.gender).all()
    # for row in evaluations:
    #     print(row[0], row[1])
    #     if row[0] == 0:
    #         gender_data.append(['Male', row[1]/total])
    #     else:
    #         gender_data.append(['Female', row[1]/total])

    data = [0, 0, 0, 0, 0]

    for i in range(5):
        for record in db.session.query(Record).all():
            if int(record.get_metrics().get('LABEL', '0')) == i + 1:
                data[i] += 1

    # 获取Evaluation的总数
    total = sum(data)
    pie_data = []
    for i in range(5):
        pie_data.append(['第' + str(i + 1) + '类', data[i] / total])

    #----------------------- 在这里填写data_map，格式为data_sample的格式 -----------------------------

#    data_map = {}
#    for evaluation in Evaluation.query.all():
#        if(evaluation.result >= 0.8):
#            addtodict3(data_map, evaluation.continent, evaluation.country, "Suspected")
#        else:
#            addtodict3(data_map, evaluation.continent, evaluation.country, "Normal")

#    print(data_map)

    # data_sample = {
    #     "Asia": {
    #         "Sri Lanka": {
    #             "Suspected": "75",
    #             "Normal": "2"
    #         },
    #         "Bangladesh": {
    #             "Suspected": "7",
    #             "Normal": "20"
    #         }
    #     },
    #     "Europe": {
    #         "Poland": {
    #             "Suspected": "1",
    #             "Normal": "0"
    #         },
    #         "Norway": {
    #             "Suspected": "1",
    #             "Normal": "0"
    #         },
    #     }
    # }
    #
    # data_map = data_sample

    #---------------------------------------------------------------------

    # 下面这一行中的 xxx=xxx 语句是把 xxx 传递到html，这样在html里就可以用 " {{ xxx }} " 的方式引用传过去的变量了
    return render_template('dashboards.html', gender_data=pie_data, data_0=data)
