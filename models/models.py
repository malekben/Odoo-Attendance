from odoo import models, fields, api
from datetime import date,datetime

# Record
class Attendance_record(models.Model):
    _name="attendance.record"
    _description="""Fingerprint input"""

    attendance_day_id=fields.Many2one("attendance.day")
    time=fields.Datetime()

# Attendance day
class Attendance_day(models.Model):
    _name="attendance.day"
    _description='''Calculate the duration of work, break,
    salary, bonus salary of a day work of an employee'''
    date=fields.Date()
    attendance_month_id=fields.Many2one('attendance.month')
    employee_id=fields.Many2one('hr.employee')
    # Create a model for lines
    lines=fields.One2many('attendance.record','attendance_day_id')
    lines_count=fields.Integer(compute="_compute_lines_count")
    # Create a compute function for all duration fields
        # Time related fields (dur=duration)
    dur=fields.Float(string='Duration',compute="_compute_dur")
    dur_break=fields.Float(string='Duration Break',compute="_compute_dur")
    dur_work=fields.Float(string='Duration work',compute="_compute_dur")
    dur_basic=fields.Float(string='Duration basic',compute="_compute_dur")
    dur_extra=fields.Float(string='Duration extra',compute="_compute_dur")
    no_break=fields.Boolean(default=False)
        # Salary related fields (slr=salary)
    to_fix=fields.Boolean(compute="_compute_to_fix")
    slr_hour=fields.Float(string="Hourly pay",compute="_compute_slr_hour")
    slr_basic=fields.Float(compute="_compute_slr_hour")
    slr_extra=fields.Float(compute="_compute_slr_hour")
    slr_total=fields.Float(compute="_compute_slr_hour")
    slr_is_paid=fields.Boolean(default=False)
    
    # compute number of lines
    @api.depends("lines")
    def _compute_lines_count(self):
        self.lines_count=len(self.lines)

    # compute Duration
    @api.depends("lines","lines_count")
    def _compute_dur(self):
        # compute duration
        x=self.lines[-1].time-self.lines[0].time
        self.dur=x.total_seconds/60

        # compute break
        if self.no_break:
            self.dur_break=0
        elif self.lines_count==4:
            y=self.lines[2].time-self.lines[1].time
            self.dur_break=y.total_seconds/60
        elif (self.lines_count==3) or (self.lines_count==2):
            self.dur_break=60
        else:
            self.dur_break=0
        
        # compute work duration
        self.dur_work=self.dur-self.dur_break

        # compute basic duration
        if self.dur_work >8*60:
            self.dur_basic=8*60
            self.dur_extra=self.dur_work-self.dur_basic
        else:
            self.dur_basic=self.dur_work
            self.dur_extra=0

    # compute salary
    @api.depends("attendance_month_id")
    def _compute_slr_hour(self):
        self.slr_hour=self.attendance_month_id.slr_hour
        self.slr_basic=self.slr_hour*(self.dur_basic/60)
        self.slr_extra=self.slr_hour*(self.dur_extra/60)
        self.slr_total=self.slr_hour*(self.dur_work/60)

    # compute to_fix
    @api.depends("dur","lines_count")
    def _compute_to_fix(self):
        if (self.dur <= 7*60) or (self.lines_count>4) or (self.lines_count==1):
            self.to_fix=True
    
# Attendance month
class Attendance_month(models.Model):
    _name="attendance.month"
    _description="""Calculation the monthly salary and all
    the indicators or the salary"""

    month=fields.Integer()
    year=fields.Integer()
    # work days means the number of days that an employee shold work in a given month
    # it depends on the number of rest days in the month and the number of days in the month
    work_days=fields.Integer(compute="_compute_work_days")
    employee_id=fields.Many2one("hr.employee")
    days_ids=fields.Many2one('attendance.days')
    leave_ids=(fields.Many2one('attendance.leave'))
    presence=fields.Integer(compute="_compute_pres_abs_leav")
    absence=fields.Integer(compute="_compute_pres_abs_leav")
    leave_count=fields.Integer(compute="_compute_pres_abs_leav")
    dur_basic=fields.Float(compute="_compute_dur_slr")
    dur_extra=fields.Float(compute="_compute_dur_slr")
    slr_hour=fields.Float(compute="_compute_slr_hour")
    slr_basic=fields.Float(compute="_compute_dur_slr")
    slr_extra=fields.Float(compute="_compute_dur_slr")
    slr_leave=fields.Float(compute="_compute_dur_slr")
    slr_total=fields.Float(compute="_compute_dur_slr")
    payments_ids=fields.Float()
    amount_due=fields.Float()
    is_paied=fields.Boolean(default=False)
    
    # compute the durations and the salary
    @api.depends("days_ids","leave_ids","slr_hour")
    def _compute_dur_slr(self):
        x=0
        y=0
        z=0
        a=0
        b=0
        if self.days:
            for day in self.days_ids:
                x+=day.dur_basic
                y+=day.dur_extra
                z+=day.slr_basic
                a+=day.slr_extra
                b+=day.slr_total
            
            # calculating leave salary
            if self.leave_ids:
                self.slr_leave=len(self.leave_ids)*self.slr_hour
            
            self.dur_basic=x
            self.dur_extra=y
            self.slr_basic=z
            self.slr_extra=a
            
            self.slr_total=b+self.slr_leave
    
    # compute the number of work days
    @api.depends("employee_id","month","year",)
    def _compute_work_days(self):
        x=self.employee_id.rest_day
        d1=date(1,self.month,self.year)
        if self.month!=12:
            d2=date(1,self.month+1,self.year)-datetime.timedelta(days=1)
        else:
            d2=date(1,1,self.year+1)-datetime.timedelta(days=1)
        # t total number of days in a month
        t=d2-d1
        # looping in month days to count the number of rest days
        # n number of rest days
        n=0
        for i in [d1,d2]:
            if i.weekday()==x:
                n+=1
        
        self.work_days=t-n

    # convert this function to a saved field not calculated 
    @api.depends("employee_id","work_days")
    def _compute_slr_hour(self):    
        self.slr_hour=self.employee_id.salary/(self.work_days*8)

    # compute presence and absence and leave_days
    @api.depends("days_ids","leave_ids","work_days")
    def _compute_pres_abs_leav(self):
        self.presence=len(self.days_ids)
        self.leave_count=len(self.leave_ids)
        self.absence=self.work_days-self.presence-self.leave_count

# Leaves
class Attendance_leave(models.Model):
    _name="attendance.leave"
    _description="""Leave record is a justified absence 
    it can be from 18 up to 21 day a year and add all
    the national holidays"""

    date=fields.Date()
    employee_id=fields.Many2one("hr.employee")
    type=fields.Selection([
        ('Holiday','holiday'),
        ('Leave','leave'),
        ('Sickness','sickness'),
    ])



# hour salary should not be a computed field,instead we should
# create a function after the instance is saved
# change to_fix field to saved field and not calculated
# fix the compute function and add the element in the field
# link all monetary activity to paiment like invoices or add a payment class
# eliminate the field lines_count