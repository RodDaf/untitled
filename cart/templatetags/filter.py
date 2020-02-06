from django.template import Library
register = Library()

@register.filter
def multiple(num1,num2):
    num1 = float(num1)
    num2 = int(num2)
    return "%.2f"%(num1*num2)

@register.filter
def sum(num1,num2):
    num1 = float(num1)
    num2 = int(num2)
    return "%.2f"%(num1+num2)