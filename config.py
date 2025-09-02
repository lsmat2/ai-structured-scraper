"""Configuration for params to Google Places API."""


# Fields that trigger Pro SKU
FIELD_MASK_TYPES_PRO = [
    'addressComponents', 
    'adrFormatAddress', 
    'attributions', 
    'businessStatus', 
    # 'containingPlaces', 
    'displayName', 
    'formattedAddress',                     
    # 'iconBackgroundColor',
    # 'iconMaskBaseUri',
    'id',
    'location',
    # 'name', # id prefixed with 'places/...'
    # 'photos',
    # 'plusCode',
    'postalAddress',
    'primaryType',
    # 'primaryTypeDisplayName',
    'shortFormattedAddress',
    'types',
    # 'viewport'
]


# Fields that trigger Enterprise SKU
FIELD_MASK_TYPES_ENTERPRISE = [
    'currentOpeningHours', 
    'currentSecondaryOpeningHours', 
    'nationalPhoneNumber', 
    'priceLevel', 
    'priceRange',
    'rating', 
    'regularOpeningHours', 
    'regularSecondaryOpeningHours', 
    'userRatingCount', 
    'websiteUri'
]


# Fields that trigger Atmosphere SKU
FIELD_MASK_TYPES_ATMOSPHERE = [
    'allowsDogs', 
    'curbsidePickup', 
    'delivery', 
    'dineIn', 
    'editorialSummary', 
    'generativeSummary', 
    'liveMusic', 
    'menuForChildren', 
    'paymentOptions', 
    'outdoorSeating', 
    'reservable', 
    'restroom', 
    'reviews', 
    'reviewSummary', 
    'servesBeer', 
    'serverBreakfast', 
    'servesBrunch', 
    'servesCocktails',
    'servesCoffee', 
    'servesDessert', 
    'servesDinner', 
    'servesLunch', 
    'servesVegetarianFood', 
    'servesWine', 
    'takeout'
]
# Combine wanted fields into a single field mask
FIELD_MASK = ','.join(f'places.{t}' for t in (FIELD_MASK_TYPES_PRO + FIELD_MASK_TYPES_ENTERPRISE))


# Types to request (max 41) from Table A types: https://developers.google.com/maps/documentation/places/web-service/place-types
INCLUDED_TYPES_FOOD_AND_DRINK = [
    'acai_shop',
    'afghani_restaurant',
    'african_restaurant',
    'american_restaurant',
    'asian_restaurant',
    'bagel_shop',
    'bakery',
    'bar',
    'bar_and_grill',
    'barbecue_restaurant',
    'brazilian_restaurant',
    'breakfast_restaurant',
    'brunch_restaurant',
    'buffet_restaurant',
    'cafe',
    'cafeteria',
    'candy_store',
    'cat_cafe',
    'chinese_restaurant',
    'chocolate_factory',
    'chocolate_shop',
    'coffee_shop',
    'confectionery',
    'deli',
    'dessert_restaurant',
    'dessert_shop',
    'diner',
    'dog_cafe',
    'donut_shop',
    'fast_food_restaurant',
    'fine_dining_restaurant',
    # 'food_court',
    # 'french_restaurant',
    # 'greek_restaurant',
    # 'hamburger_restaurant',
    # 'ice_cream_shop',
    # 'indian_restaurant',
    # 'indonesian_restaurant',
    # 'italian_restaurant',
    # 'japanese_restaurant',
    'juice_shop',
    # 'korean_restaurant',
    # 'lebanese_restaurant',
    # 'meal_delivery',
    # 'meal_takeaway',
    # 'mediterranean_restaurant',
    'mexican_restaurant',
    # 'middle_eastern_restaurant',
    'pizza_restaurant',
    'pub',
    'ramen_restaurant',
    'restaurant',
    'sandwich_shop',
    # 'seafood_restaurant',
    # 'spanish_restaurant',
    'steak_house',
    # 'sushi_restaurant',
    'tea_house',
    # 'thai_restaurant',
    # 'turkish_restaurant',
    # 'vegan_restaurant',
    # 'vegetarian_restaurant',
    # 'vietnamese_restaurant',
    'wine_bar'
]