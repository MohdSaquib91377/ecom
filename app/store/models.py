from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from config.base import TimeStampModel
import PIL.Image
from accounts.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver


class Category(TimeStampModel):
    image = models.ImageField(upload_to = 'category/',max_length=255, blank=True, null=True)
    name = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
     


class SubCategory(TimeStampModel):
    image = models.ImageField(upload_to = 'sub_category/',max_length=255, blank=True, null=True)
    name = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey("Category",on_delete = models.CASCADE,related_name = "sub_categories",null= True)
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
     
    def __str__(self) -> str:
        return f"{self.name}"

class Brand(TimeStampModel):
    name = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Product(TimeStampModel):
    name = models.CharField(max_length=64)
    sku = models.CharField(max_length=64)
    price = models.FloatField(validators=[MinValueValidator(0.0)],default=0.0)
    old_price = models.FloatField(validators=[MinValueValidator(0.0)],default=0.0,blank=True)
    is_active = models.BooleanField(default=True)
    quantity = models.PositiveIntegerField()
    description = models.TextField()
    category = models.ForeignKey('Category',on_delete=models.CASCADE,related_name="products",null=True,blank=True)
    sub_category = models.ForeignKey('SubCategory',on_delete=models.CASCADE,related_name="products",null=True,blank=True)
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE,related_name="products",null=True,blank=True)
    class Meta:
        db_table = "products"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.id} -> {self.name} -> {self.sub_category.name} -> {self.category.name}"

    def clean(self):
        sub_category_list = SubCategory.objects.filter(category = self.category).values_list("id",flat = True)
        if not self.sub_category_id in sub_category_list:
            raise ValidationError("Sub Category does not match for category")
        super(Product, self).clean()



class Image(TimeStampModel):
    image = models.ImageField(upload_to='images/products/main/',default = "fabfarm.jpg")
    products = models.ForeignKey("Product",on_delete=models.CASCADE,related_name='images')

    class Meta:
        ordering = ['-created_at']
         
    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)
        img = PIL.Image.open(self.image.path)
        output_size = (500,400)
        img.thumbnail(output_size)
        img.save(self.image.path)



class Wishlist(TimeStampModel):
    product = models.ForeignKey(Product,related_name = "wishlist", on_delete = models.CASCADE)
    user = models.ForeignKey("accounts.User",related_name = "wishlist", on_delete = models.CASCADE)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name}"


    
class RecentView(TimeStampModel):
    user = models.ForeignKey("accounts.User",on_delete=models.CASCADE,related_name="recent_views")
    product = models.ForeignKey("Product",on_delete=models.CASCADE,related_name="recent_views")
    views_counter = models.IntegerField(default=1)

    class Meta:
        ordering = ["-created_at"]

