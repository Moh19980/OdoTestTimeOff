from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    @api.model
    def create(self, vals):
        leave = super(HrLeave, self).create(vals)
        leave._check_and_update_vacation_balance()
        return leave

    def _check_and_update_vacation_balance(self):
        for leave in self:
            if leave.holiday_status_id.name == 'Time Off' and leave.duration_display > 7:
                employee = leave.employee_id
                vacation_days = self.env['hr.leave.type'].search(
                    [('name', '=', 'Vacation')], limit=1)
                if not vacation_days:
                    raise ValidationError("No 'Vacation' leave type found.")

                # Assuming 1 day equals 8 hours
                leave_duration_in_days = leave.duration_display / 5
                if leave_duration_in_days > 0:
                    leave_days_record = self.env['hr.leave.allocation'].search([
                        ('employee_id', '=', employee.id),
                        ('holiday_status_id', '=', vacation_days.id),
                        ('state', '=', 'validate')
                    ], limit=1)

                    if leave_days_record:
                        leave_days_record.write({
                            'number_of_days': leave_days_record.number_of_days - 1
                        })
                    else:
                        raise ValidationError(
                            f"No validated vacation leave allocation found for {employee.name}.")
