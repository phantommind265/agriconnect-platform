from flask import Blueprint, render_template, request, redirect, url_for, flash
import json
from flask_login import login_required
from datetime import datetime
from agriplatform.utils.translator import t
from config import PRICES_DATA_PATH
from agriplatform.forms.profit_form import ProfitEstimateForm

market_bp = Blueprint('market', __name__, template_folder='../templates/market')

#load price data
def load_prices():
    with open(PRICES_DATA_PATH, 'r') as f:
        return json.load(f)
    
#Route: view market prices(basic table or summary)
@market_bp.route('/market')
@login_required
def market_prices():
    prices = load_prices()
    return render_template('market/market.html', prices=prices, t=t)

#Route: estimate profit(form input and result)
"""
@market_bp.route('/estimate', methods=['GET', 'POST'])
def estimate_profit():
    prices = load_prices()
    crops = [item['crop'] for item in prices]  #extract crop names from the list

    if request.method == 'POST':
        crop = request.form.get('crop')
        area = float(request.form.get('area'))
        cost = float(request.form.get('cost'))
        yield_per_acre = float(request.form.get('yield'))
        month = request.form.get('month').capitalize()

        #find the crops
        crop_prices = next((item['prices'] for item in prices if item['crop'] == crop), None)
        if not crop_prices:
            flash(t("crop_not_found"), "error")
            return redirect(url_for('market.estimate_profit'))

        #get the price from the selected month
        price = crop_prices.get(month)
        if not price:
            flash(t("price_not_found_for_month"), "error")
            return redirect(url_for('market.estimate_profit'))

        #perform calculations
            
        total_yield = area * yield_per_acre * 1000 #convert tons to kg
        revenue = total_yield * price
        profit = revenue - cost

        return render_template(
            'market/estimate_result.html',
            t=t, 
            crop=crop, 
            revenue=round(revenue, 2), 
            cost=round(cost, 2), 
            profit=round(profit, 2),
            month=month,
            area=area,
            yield_per_acre=yield_per_acre
        )
        
    return render_template('market/estimate_profit.html', crops=crops, t=t)
"""

@market_bp.route('/estimate', methods=['GET', 'POST'])
@login_required
def estimate_profit():
    prices = load_prices()
    crops = [item['crop'] for item in prices]  # extract crop names from the list

    form = ProfitEstimateForm()
    form.crop.choices = [(c, c) for c in crops]  # populate dropdown

    if form.validate_on_submit():
        crop = form.crop.data
        area = form.area.data
        cost = form.cost.data
        yield_per_acre = form.yield_per_acre.data
        month = form.month.data.capitalize()

        # find the crop prices
        crop_prices = next((item['prices'] for item in prices if item['crop'] == crop), None)
        if not crop_prices:
            flash(t("crop_not_found"), "error")
            return redirect(url_for('market.estimate_profit'))

        # get price from the selected month
        price = crop_prices.get(month)
        if not price:
            flash(t("price_not_found_for_month"), "error")
            return redirect(url_for('market.estimate_profit'))

        # perform calculations
        total_yield = area * yield_per_acre * 1000  # tons → kg
        revenue = total_yield * price
        profit = revenue - cost

        return render_template(
            'market/estimate_result.html',
            t=t,
            crop=crop,
            revenue=round(revenue, 2),
            cost=round(cost, 2),
            profit=round(profit, 2),
            month=month,
            area=area,
            yield_per_acre=yield_per_acre
        )

    return render_template('market/estimate_profit.html', form=form, t=t)


#Route: price trends chart
@market_bp.route('/price_trend/<crop>')
def price_trend(crop):
    prices = load_prices()
    crop_data = next((item for item in prices if item['crop'] == crop), None)
    if not crop_data:
        flash(t("crop_not_found"), "error")
        return redirect(url_for('market.market_prices'))
    
    months = list(crop_data['prices'].keys())
    price_values = list(crop_data['prices'].values())

    return render_template(
            'market/price_trend.html', 
            crop=crop, 
            months=months, 
            prices=price_values, 
            t=t
        )
