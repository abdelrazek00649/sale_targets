from odoo import models, fields, api
from datetime import date, timedelta

class SaleTarget(models.Model):
    _name = 'sale.target'
    _description = 'Sales Target'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='اسم الهدف', required=True, tracking=True)

    salesperson_id = fields.Many2one(
        'res.users',
        string='مندوب المبيعات',
        required=True,
        tracking=True
    )

    target_amount = fields.Float(
        string='الهدف المطلوب',
        required=True,
        tracking=True
    )

    actual_amount = fields.Float(
        string='المبيعات الفعلية',
        compute='_compute_actual_amount',
        store=True
    )

    achievement = fields.Float(
        string='نسبة الإنجاز %',
        compute='_compute_achievement',
        store=True
    )

    reward_amount = fields.Float(
        string='المكافأة',
        compute='_compute_reward',
        store=True
    )

    daily_target = fields.Float(
        string='الهدف اليومي المطلوب',
        compute='_compute_daily_target',
        store=True
    )

    days_remaining = fields.Integer(
        string='الأيام المتبقية',
        compute='_compute_daily_target',
        store=True
    )

    date_from = fields.Date(
        string='من التاريخ',
        required=True,
        default=lambda self: date.today().replace(day=1)
    )

    date_to = fields.Date(
        string='حتى التاريخ',
        required=True
    )

    state = fields.Selection([
        ('draft', 'مسودة'),
        ('active', 'نشط'),
        ('done', 'تم'),
    ], default='draft', string='الحالة', tracking=True)

    @api.depends('salesperson_id', 'date_from', 'date_to')
    def _compute_actual_amount(self):
        for rec in self:
            if rec.salesperson_id and rec.date_from and rec.date_to:
                orders = self.env['sale.order'].search([
                    ('user_id', '=', rec.salesperson_id.id),
                    ('state', 'in', ['sale', 'done']),
                    ('date_order', '>=', str(rec.date_from)),
                    ('date_order', '<=', str(rec.date_to)),
                ])
                rec.actual_amount = sum(orders.mapped('amount_total'))
            else:
                rec.actual_amount = 0.0

    @api.depends('target_amount', 'actual_amount')
    def _compute_achievement(self):
        for rec in self:
            if rec.target_amount > 0:
                rec.achievement = (rec.actual_amount / rec.target_amount) * 100
            else:
                rec.achievement = 0.0

    @api.depends('achievement', 'target_amount')
    def _compute_reward(self):
        for rec in self:
            if rec.achievement >= 100:
                rec.reward_amount = rec.target_amount * 0.05
            elif rec.achievement >= 75:
                rec.reward_amount = rec.target_amount * 0.03
            elif rec.achievement >= 50:
                rec.reward_amount = rec.target_amount * 0.01
            else:
                rec.reward_amount = 0.0

    @api.depends('target_amount', 'actual_amount', 'date_to')
    def _compute_daily_target(self):
        for rec in self:
            today = date.today()
            if rec.date_to and rec.date_to >= today:
                rec.days_remaining = (rec.date_to - today).days + 1
                remaining_amount = rec.target_amount - rec.actual_amount
                if rec.days_remaining > 0 and remaining_amount > 0:
                    rec.daily_target = remaining_amount / rec.days_remaining
                else:
                    rec.daily_target = 0.0
            else:
                rec.days_remaining = 0
                rec.daily_target = 0.0

    def action_set_active(self):
        self.state = 'active'
        self.message_post(body="✅ تم تفعيل الهدف")

    def action_set_done(self):
        self.state = 'done'
        self._send_achievement_email()
        self.message_post(body=f"🏁 تم إنهاء الهدف - نسبة الإنجاز: {self.achievement:.1f}%")

    def action_check_warnings(self):
        """تحقق من التنبيهات وأرسلها"""
        for rec in self:
            today = date.today()
            if rec.date_from and rec.date_to and rec.state == 'active':
                total_days = (rec.date_to - rec.date_from).days
                passed_days = (today - rec.date_from).days
                if total_days > 0:
                    time_passed_pct = (passed_days / total_days) * 100
                    # تحذير: عدى نص الشهر وعنده أقل من 40%
                    if time_passed_pct >= 50 and rec.achievement < 40:
                        rec.message_post(
                            body=f"⚠️ تحذير: مضى {time_passed_pct:.0f}% من الوقت ونسبة الإنجاز {rec.achievement:.1f}% فقط!",
                            partner_ids=[rec.salesperson_id.partner_id.id]
                        )
                    # تنبيه: وصل للهدف
                    if rec.achievement >= 100:
                        rec.message_post(
                            body=f"🏆 مبروك! حققت هدفك بنسبة {rec.achievement:.1f}%! مكافأتك: {rec.reward_amount:.2f}",
                            partner_ids=[rec.salesperson_id.partner_id.id]
                        )

    def _send_achievement_email(self):
        for rec in self:
            if rec.salesperson_id.email:
                mail_vals = {
                    'subject': '🏆 مبروك! حققت هدفك!',
                    'body_html': f'''
                        <div style="font-family:Arial; padding:20px; background:#f9f9f9;">
                            <h2 style="color:#00a09d;">مبروك {rec.salesperson_id.name}! 🎉</h2>
                            <p>لقد أنهيت الهدف بنتائج رائعة:</p>
                            <table style="width:100%; border-collapse:collapse;">
                                <tr style="background:#00a09d; color:white;">
                                    <td style="padding:10px;">البيان</td>
                                    <td style="padding:10px;">القيمة</td>
                                </tr>
                                <tr>
                                    <td style="padding:10px; border:1px solid #ddd;">الهدف المطلوب</td>
                                    <td style="padding:10px; border:1px solid #ddd;">{rec.target_amount:,.2f}</td>
                                </tr>
                                <tr>
                                    <td style="padding:10px; border:1px solid #ddd;">المبيعات الفعلية</td>
                                    <td style="padding:10px; border:1px solid #ddd;">{rec.actual_amount:,.2f}</td>
                                </tr>
                                <tr>
                                    <td style="padding:10px; border:1px solid #ddd;">نسبة الإنجاز</td>
                                    <td style="padding:10px; border:1px solid #ddd;">{rec.achievement:.1f}%</td>
                                </tr>
                                <tr style="background:#e8f8f5;">
                                    <td style="padding:10px; border:1px solid #ddd;"><strong>المكافأة المستحقة</strong></td>
                                    <td style="padding:10px; border:1px solid #ddd;"><strong>{rec.reward_amount:,.2f}</strong></td>
                                </tr>
                            </table>
                        </div>
                    ''',
                    'email_to': rec.salesperson_id.email,
                    'email_from': self.env.user.email or 'noreply@company.com',
                }
                mail = self.env['mail.mail'].create(mail_vals)
                mail.send()