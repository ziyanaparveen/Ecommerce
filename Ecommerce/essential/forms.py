from django import forms
from .models import *


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        
        
    def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs) 
            
            for label,field in self.fields.items():
                field.widget.attrs.update({
                    'class':'form-control'
                },)
                
                
class CheckoutForm(forms.ModelForm): 
    class Meta:
        model = CheckoutAddress
        fields = ['street_address','apartment_address','country','zip_code']  
        
        
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs) 
        
        for label,field in self.fields.items():
            field.widget.attrs.update({
                'class':'form-control'
            },)                  
                    