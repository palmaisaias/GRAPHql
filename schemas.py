import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import Product as ProductModel, db

class Product(SQLAlchemyObjectType):
    class Meta:
        model = ProductModel

class Query(graphene.ObjectType):
    products = graphene.List(Product)
    search_products = graphene.List(Product, name=graphene.String(), price= graphene.Float(), category= graphene.String())
    

    def resolve_products(self, info):
        return db.session.execute(db.select(ProductModel)).scalars()
    
    def resolve_search_products(self, info, name=None, category=None):
        query = db.select(ProductModel)

        if name:
            query = query.where(ProductModel.name.ilike(f'%{name}%'))
        if category:
            query = query.where(ProductModel.category.ilike(f'%{category}%'))

        result = db.session.execute(query).scalars().all()
        return result  

class AddProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        category = graphene.String(required=True)

    product = graphene.Field(Product)

    def mutate(self, info, name, price, category):
        product = ProductModel(name=name, price=price, category=category)
        db.session.add(product)
        db.session.commit()

        db.session.refresh(product)
        return AddProduct(product=product)  

class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        price = graphene.Float()
        category = graphene.String()

    product = graphene.Field(Product)

    def mutate(self, info, id, name=None, price=None, category=None):
        product = db.session.get(ProductModel, id)

        if not product:
            return None
        if name:
            product.name = name
        if price:
            product.price = price
        if category:
            product.category = category

        db.session.add(product)
        db.session.commit()

        db.session.refresh(product)
        return UpdateProduct(product=product)
    
class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    product = graphene.Field(Product)

    def mutate(self, info, id):
        product = db.session.get(ProductModel, id)

        if product:
            db.session.delete(product)
            db.session.commit()
        else:
            return None

        return DeleteProduct(product=product)

class Mutation(graphene.ObjectType):
    bake_product = AddProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
