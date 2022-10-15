from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date,datetime, timedelta

def excel_date_format(date):
    offset = 693594
    n = date
    return (n - offset)

# Record
class Attendance_record(models.Model):
    _name="attendance.record"
    _description="""Fingerprint input"""
    _order="time,day_id"
    name = fields.Char(compute="_compute_name")
    day_id=fields.Many2one("attendance.day",ondelete="cascade")
    time=fields.Datetime(default=lambda self: self._default_date())

    def _compute_name(self):
        for record in self:
            if record.day_id:
                record.name= record.day_id.name
            else:
                record.name = ""

    def _default_date(self):
        if self.day_id:
            d=self.day_id.date
            time=datetime.combine(d,datetime.min.time(),required=True)
        else:
            time=datetime.now()

        return time

# Attendance day
class Attendance_day(models.Model):
    _name="attendance.day"
    _description='''Calculate the duration of work, break,
    salary, bonus salary of a day work of an employee'''
    _order = "date desc,month_id"
    # Fields
    
    name=fields.Char(compute="_compute_name")
    date=fields.Date()
    month_id=fields.Many2one('attendance.month')
    lines=fields.One2many('attendance.record','day_id',ondelete="cascade")
    line_count=fields.Integer(compute="_compute_line_count")
    check_in=fields.Char(compute="_compute_check_in_out")
    check_out=fields.Char(compute="_compute_check_in_out")
    
    # Time related fields (dur=duration)
    dur_total=fields.Float(string='Duration',compute="_compute_dur",readonly=True,default=0)
    dur_break=fields.Float(string='Duration Break',compute="_compute_dur",readonly=True,default=0)
    dur_work=fields.Float(string='Duration work',compute="_compute_dur",readonly=True,default=0)
    
    # Check field
    to_fix=fields.Boolean(default=False)
    no_break=fields.Boolean(default=False)
    type=fields.Selection([
        ('presence','Presence'),
        ('rest_day','Rest day'),
        ('holiday','Holiday'),
        ('absent','Absent')
    ],required=True,default='presence')
    # Compute functions
    # Compute name
    @api.depends("month_id")
    def _compute_name(self):
        for record in self:
            if record.month_id.employee_id:
                record.name = record.month_id.employee_id.name
            else:
                record.name = ""
    
    # compute line count
    def _compute_line_count(self):
        for record in self:
            record.line_count = len(record.lines)
    
    # compute check in out
    def _compute_check_in_out(self):
        for record in self:
            if record.lines:
                record.check_in = datetime.strftime(record.lines[0].time,"%H:%M:%S")
                record.check_out = datetime.strftime(record.lines[-1].time,"%H:%M:%S")
            else:
                record.check_in = False
                record.check_out = False
        
    # compute Duration
    @api.depends("lines")
    def _compute_dur(self):
        for record in self:
            # compute duration
            if len(record.lines)>=2 and len(record)<=4:
                x=record.lines[-1].time-record.lines[0].time
                record.dur_total=x.total_seconds()/(60*60)
            else:
                record.dur_total=0

            # compute break
            if record.no_break:
                record.dur_break=0
            else:
                if len(record.lines)==4:
                    y=record.lines[2].time-record.lines[1].time
                    record.dur_break=y.total_seconds()/(60*60)
                elif (len(record.lines)==3) or (len(record.lines)==2):
                    record.dur_break=1
                else:
                    record.dur_break=0
        
            # compute work duration
            record.dur_work=record.dur_total-record.dur_break

    
    # Onchange functions
    @api.onchange("lines")
    def _organize_time(self):
        for record in self:
            for i in range(0,len(record.lines)-1):
                j=len(record.lines)-1-i
                if (record.lines[j].time<record.lines[j-1].time) and (j!=0):
                    t=record.lines[j-1].time
                    record.lines[j-1].time=record.lines[j].time
                    record.lines[j].time=t

# Attendance month
class Attendance_month(models.Model):
    _name="attendance.month"
    _description="""Calculation the monthly salary and all
    the indicators or the salary"""
    _order="month desc,year,employee_id"

    name=fields.Char()
    employee_id=fields.Many2one("hr.employee")
    month=fields.Integer(required=True)
    year=fields.Integer(required=True)
    days_ids=fields.One2many('attendance.day','month_id',ondelete="cascade")
   
    rest_day=fields.Integer(default=0)
    rest_day_name=fields.Char(compute="_compute_rest_day_name",readonly=True,default="")
    
    total_days=fields.Integer(compute="_compute_work_rest_total_days",readonly=True,default=0)
    work_days=fields.Integer(compute="_compute_work_rest_total_days",readonly=True,default=0)
    presence=fields.Integer(readonly=True,default=0)
    rest_days=fields.Integer(compute="_compute_work_rest_total_days",readonly=True,default=0)
    abseence=fields.Integer(readonly=True,default=0)
    holidays=fields.Integer()
    
    dur_basic=fields.Float(readonly=True,default=0)
    dur_extra=fields.Float(readonly=True,default=0)
    

    # Compute functions
     
    # compute rest day name
    @api.depends("rest_day")
    def _compute_rest_day_name(self):
        dayName=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        for record in self:
            record.rest_day_name=dayName[record.rest_day]

    # compute work days 
    @api.depends("month","year","rest_day")
    def _compute_work_rest_total_days(self):
        for record in self:
            if record.month and record.year:
                x=record.rest_day
                d1=date(record.year,record.month,1)
                if record.month!=12:
                    d2=date(record.year,record.month+1,1)- timedelta(days=1)
                else:
                    d2=date(record.year+1,1,1,)-datetime.timedelta(days=1)
                # t total number of days in a month
                t=d2-d1
                # looping in month days to count the number of rest days
                # n number of rest days
                n=0
                d=d1
                while d<=d2:
                    if d.weekday()==x:
                        n+=1
                    d+=timedelta(days=1)
                
                print('rest days',n)
                
                record['total_days']=t.days+1
                record['rest_days']=n
                record['work_days']=t.days+1-n
                
            else:
                record['total_days']=0
                record['rest_days']=0
                record['work_days']=0

    # On creation function
    # calculated work days and bring the month salary from hr.employee
    @api.model
    def create(self,vals): 
        record= super(Attendance_month,self).create(vals)
        # Calculating work days
        if record.employee_id.rest_day and record['total_days']:
            # calculating hour salary
            record['rest_day']=record.employee_id.rest_day
            
        return record
    
    # Actions
    # Identify the wrong attendance days
    def action_scan_to_fix(self):
        for record in self:
            for day in record.days_ids:
                if len(day.lines)>4 or len(day.lines)<2 or day.dur<7:
                    day.to_fix=True
            
        return True

    def action_complete_records(self):
        for record in self:
            for i in range(1,record['total_days']+1):
                d= date(record.year,record.month,i)
                holiday = record.env['attendance.holiday'].search([
                    ('date','=',d)
                ])
                if d.weekday()==record.rest_day:
                    type="rest_day"
                elif holiday:
                    type="holiday"
                else:
                    type="absent"
                data = record.days_ids.search([
                    ('month_id','=',record.id),
                    ('date','=',d)
                ])
                if data:
                    data.type=type
                else:
                    record.days_ids.create({
                        "date":d,
                        "month_id":record.id,
                        "type":type
                    })


   

# Holidays
class AttendanceHoliday(models.Model):
    _name="attendance.holiday"

    name=fields.Char(required=True)
    date=fields.Date(required=True)
    days = fields.Integer(default=1,required=True)

# HR employee
class HrEmployee(models.Model):
    _inherit="hr.employee"
    acs_code = fields.Char(unique=True)
    rest_day=fields.Integer()
    salary=fields.Float()

    # Constrains function
    @api.constrains('rest_day')
    def _check_rest_day(self):
        for record in self:
            if (record.rest_day<1) or (record.rest_day>7):
                raise ValidationError('The rest day should be a number between 1 and 7')
    
    @api.constrains('salary')
    def _check_salary(self):
        for record in self:
            if record.salary<0:
                raise ValidationError('The salary should be a positive number')


# Change the name of Leave to absence (absence can be a leave in selection field)
# Coorect the function action_scan_abs
# fix the constrains function
# Change total salary to saved field and not calculated field
# fix the amount_due and the amount_paid onchange function
# add an on delete fonctionality in One2many fields (to delete)
# Create holiday model
# Fix the constrains functions
# change the rest_day to saved field and work_days to computed fields

# link all monetary activity to paiment like invoices or add a payment class
# attendance day record name should be employee_name+weekday(in letters)+date
# attendance month record name should be employee_name+month(in letters)
# Correct the no break function