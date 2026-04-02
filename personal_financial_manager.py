import matplotlib.pyplot as plt
from datetime import datetime
import csv
import json
import os

#-----SAVE USER PROFILE-----
def save_user_profile(profile):
    with open("user_profile.json","w") as file:
        json.dump(profile,file,indent=4)
        
#-----load user profile-----
def load_user_profile():
    if not os.path.exists("user_profile.json"):
        return None
    with open("user_profile.json","r") as file:
        return json.load(file)

def get_salary():
    salary=float(input("Enter your monthly salary: "))
    return salary
    

def get_fixed_expenses():
    fixed_expenses={}
    
    while True:
      name=input("Enter fixed expense name(or type 'done'): ")
      if name.lower()=="done":
        break
      amount=float((input("Enter amount: ")))
      fixed_expenses[name]=amount
    return fixed_expenses

def set_spending_limit(profile):
    salary=profile["salary"]
    fixed_expenses=profile["fixed_expenses"]
    #------SUMMARY OF FIXED EXPENSES-------
    print("\n-------Fixed Expense Summary------")

    for name,amount in fixed_expenses.items():
        print(name,":",amount)

    total_fixed=sum(fixed_expenses.values())

    remaining_money=salary-total_fixed
    print("Money left after fixed expenses is:",remaining_money)
    
    #if limit is already saved
    if "limit" in profile:
        print("Your saved spending limit:",profile["limit"])
        return remaining_money,profile["limit"]
    #Ask limit first time only
    limit=float(input("Enter your monthly spending limit="))

    while limit>remaining_money:
        print("Limit cannot exceed remaining money.")
        limit=float(input("Enter your monthly spending limit again: "))        
    #save limit into profile
    profile["limit"]=limit
    save_user_profile(profile)
    
    return remaining_money,limit
 #for completed weeks
def get_completed_weeks():
     completed=set()
     if os.path.exists("weekly_expenses.csv"):
         with open("weekly_expenses.csv","r") as file:
             reader=csv.reader(file)
             next(reader,None)
             
             for row in reader:
                 completed.add(row[0])
     return completed
        
def track_weekly_expenses(limit,total_spend):
    category_totals = {}
    weekly_totals = {}

    completed_weeks = get_completed_weeks()

    # Find next week number
    if completed_weeks:
        next_week=max([int(w.replace("Week",""))for w in completed_weeks])+1
    else:
        next_week=1
    if next_week>4:
        print("All 4 weeks are already entered.")
        return total_spend, category_totals,{},{}


    start = input(f"\nEnter expenses for Week {next_week}? (yes/done): ")

    if start.lower() == "done":
        return total_spend, category_totals,{},{}

    print(f"\n--- Week {next_week} Expenses ---")

    week_total = 0
    week_data={}

    while True:

        category = input("Enter category (or type 'done'): ")
        category=category.lower()

        if category.lower() == "done":
            break

        amount = float(input("Enter amount: "))

        week_total += amount
        total_spend += amount
        if category in week_data:
         week_data[category]+=amount
        else:
            week_data[category]=amount
        
        #----LIMIT WARNING CHECK----
        if total_spend>=0.8*limit and total_spend<=limit:
            print("Warning:You have used 80% of your spending limit!! ")
        elif total_spend>limit:
            print("🚨 Limit Exceeded!")

        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount
    
    weekly_totals[f"Week{next_week}"] = week_total
    week_data_dict={f"Week{next_week}":week_data}

    print(f"Total for Week {next_week}: {week_total}")


    return total_spend, category_totals, week_data_dict,weekly_totals
   
            
#-------SUMMARY------- 
def show_summary(category_totals,total_spend,remaining_money):
    print("\n Category Spending Summary")

    for category,amount in category_totals.items():
     print(category, ":", amount)
    print("\n Total spending: ",total_spend)   
#-----HIGHEST SPENDING CATEGORY----
    if category_totals:
     highest_category=max(category_totals,key=category_totals.get)
     highest_amount=category_totals[highest_category]
     print("\nHighest spending category:",highest_category,"(",highest_amount,")") 
    else:
        print("\n No data available")

#----MONTHLY SAVINGS PREDICTION----
    savings=remaining_money-total_spend

    print("\nEstimated savings this month:",savings)
    if savings>0:
      print("Good! You saved money this month.")
    elif savings==0:
      print("You spent exactly your remaining money.")
    else:
     print("Warning: You overspent this month!")
     
    return savings
    
def save_month_data(total_spend,savings):
    month=datetime.now().strftime("%B")
    
    file_exists=False
    try:
     with open("finance_history.csv","r"):
         file_exists=True
    except FileNotFoundError:
        file_exists=False
    
    with open("finance_history.csv","a",newline="") as file:
        writer=csv.writer(file)
        
        if not file_exists:
            writer.writerow(["Month","Totalspend","savings"])
            
        writer.writerow([month,total_spend,savings])
    
    print("\n Monthly data saved successfully!")

    
 
#----LOAD WEEKLY DATA------
def load_weekly_data():
    weekly_data={}
    if os.path.exists("weekly_expenses.csv"):
        with open("weekly_expenses.csv","r") as file:
            reader=csv.reader(file)
            next(reader,None)
            
            for row in reader:
                week=row[0]
                amount=float(row[2])
                if week in weekly_data:
                    weekly_data[week]+=amount
                else:
                    weekly_data[week]=amount
    return weekly_data

#-------LOAD CATEGORY DATA------
def load_category_data():
    import csv
    import os

    category_totals = {}

    if os.path.exists("weekly_expenses.csv"):
        with open("weekly_expenses.csv","r") as file:
            reader = csv.reader(file)
            next(reader, None)

            for row in reader:
                category = row[1]
                amount = float(row[2])

                if category in category_totals:
                    category_totals[category] += amount
                else:
                    category_totals[category] = amount

    return category_totals

#-----SAVE WEEKLY DATA-----
def save_weekly_data(week_data):
    file_exists=os.path.exists("weekly_expenses.csv")
    
    with open("weekly_expenses.csv","a",newline="") as file:
        writer=csv.writer(file)
        
        if not file_exists:
            writer.writerow(["Week","Category","Amount"])
        for week,categories in week_data.items():
            for cat,amt in categories.items():
                writer.writerow([week,cat,amt])
                
#-----FUNCTION TO LOAD GOALS-----    
def load_goals():

    # If goals.json does not exist, create it
    if not os.path.exists("goals.json"):
        with open("goals.json", "w") as file:
            json.dump([], file)
        return []

    # If file exists, read it
    with open("goals.json", "r") as file:
        return json.load(file)
    
#-----FUNCTION TO SHOW EXISTING GOAL
def show_goals(goals):
    #check if goals list is empty
    if len(goals)==0:
        print("\nNo goals added yet.")
        return
    print("\n Your current goals ")
    
    for i,g in enumerate(goals,start=1):
        goal_name=g["goal"]
        price=g["price"]
        saved=g["saved"]
        
        print(f"{i}.{goal_name}-saved {saved}/{price}")
    
#FUNCTION TO ADD GOALS
def add_goal(goals):
    print("ADD NEW GOAL")
    while True:
        
      #check goal limit
     if len(goals)>=5:
        print("Goal limit reached(Maximum 5 goals allowed)")
        break 
     goal_name=input("Enter goal name or (type done for no goals):")
     if goal_name.lower()=="done":
       break
    
     price=int(input("Enter goal price:"))
     saved=int(input("Enter amount already saved:"))
    
    
    #dictionary for goal
     new_goal={
        "goal":goal_name,
        "price":price,
        "saved":saved
    }
     #add to goals list
     goals.append(new_goal)
     print("Goal added successfully!")
    return goals

#function to save goals
def save_goals(goals):
    #write goals list into goals.json
    with open("goals.json","w") as file:
        json.dump(goals,file,indent=4)
        
    print("Goals saved successfully!")
    
#Goals estimate
def estimate_goal_time(goals,savings,remaining_money,total_spend):
    
    print("\nGoal Predictions")
    #calculate savings if user didn't run summmary
    if savings is None:
        print("Run summary first to calclate savings.")
        return
    if savings<=0:
        savings=remaining_money-total_spend
    if len(goals)==0:
        print("No goals added yet.")
        return
    saving_per_goal=savings/len(goals)
    for g in goals:
        goal_name=g["goal"]
        price=g["price"]
        saved=g["saved"]
        
        remaining=price-saved
        if price==0:
            progress=0
        else:
         progress=(saved/price)*100
        
        print("\nGoal:",goal_name)
        print("Total price:",price)
        print("Already saved:",saved)
        print("Progress:",round(progress,2),"%")
        
        #Goal complition check
        if saved>=price:
            print("✅ Goal Achieved!")
            continue
        
        if saving_per_goal>0:
            months=remaining/saving_per_goal
            print("Estimated months remaining:",round(months,1))        
            
        else:
           print("You are not saving money currently.cannot estimate time.")
        
        
    
    
#----WHAT IF SIMULATOR
def what_if_simulator(goals,savings):
    
    print("\n WHAT-IF SIMULATOR")
    extra=int(input("Enter extra savings per month you want to try:"))
    new_savings=savings+extra
    
    if len(goals)==0:
        print("No goals available for simulation.")
        return
    
    saving_per_goal=new_savings/len(goals)
    
    for g in goals:
        goal_name=g["goal"]
        price=g["price"]
        saved=g["saved"]
        
        remaining=price-saved
        
        if remaining<=0:
            print(f"\n{goal_name} already achieved.")
            continue
        
        months=remaining/saving_per_goal
        
        print(f"\nGoal:{goal_name}")
        print("If you save extra",extra,"per month")
        print("New estimated months:",round(months))
   
#-------FINANCIAL ADVISOR-----
def financial_advisor(category_totals,savings):
    print("\n--------Financial Advice------")
    if not category_totals:
        print("No expense data available yet.")
        return
    #highest spending category
    highest_category=max(category_totals,key=category_totals.get)
    highest_amount=category_totals[highest_category]
    
    print("Your highest spending category is:",highest_category,"(",highest_amount,")")
    
    suggested_saving=highest_amount*0.10
    
    print("Try reducing",highest_category,"Expenses by 10% to save",suggested_saving)
    
    #saving advice
    if savings>0:
        print("Good job! You saved money this month.")
        print("Keep saving to achieve your goals faster.")
        
    elif savings==0:
        print("You spent all remaining money.try saving some next month.")
        
    else:
        print("Warning: You overspent this month.")
        print("Reduce unnecessary expenses.") 
        
#------SPENDING PREDICTION------
def spending_prediction(remaining_money): 
    try:
        weekly_data = {}

        # ---- LOAD DATA FROM CSV ----
        if os.path.exists("weekly_expenses.csv"):
            with open("weekly_expenses.csv", "r") as file:
                reader = csv.reader(file)
                next(reader, None)

                for row in reader:
                    week = row[0]
                    amount = float(row[2])

                    if week in weekly_data:
                        weekly_data[week] += amount
                    else:
                        weekly_data[week] = amount

        # ---- CONVERT TO ORDERED LIST ----
        weeks = [weekly_data[f"Week{i}"] for i in range(1,5) if f"Week{i}" in weekly_data]

        if len(weeks) == 0:
            print("No data for prediction")
            return

        # ---- AVERAGE BASED ----
        avg_week = sum(weeks) / len(weeks)
        avg_prediction = avg_week * 4

        # ---- TREND BASED ----
        if len(weeks) >= 2:
            trend = (weeks[-1] - weeks[0]) * 0.2
        else:
            trend = 0

        trend_week = avg_week + trend
        trend_prediction = trend_week * 4

        # ---- OUTPUT ----
        print("\n------Next Month Prediction------")

        print("\n📊 Average-Based Prediction:")
        print("Predicted spending:", round(avg_prediction, 2))
        print("Predicted savings:", round(remaining_money- avg_prediction, 2))

        print("\n📉 Trend-Based Prediction:")
        print("Predicted spending:", round(trend_prediction, 2))
        print("Predicted savings:", round(remaining_money - trend_prediction, 2))

        # ---- INSIGHT ----
        if trend_prediction < avg_prediction:
            print("\n✅ Good trend: Your spending is decreasing!")
        elif trend_prediction > avg_prediction:
            print("\n⚠️ Warning: Your spending is increasing!")
        else:
            print("\n➡️ Your spending is stable.")

    except Exception as e:
        print("Error in prediction:", e)
    
        
    
def show_graphs(weekly_totals,category_totals):
    if not weekly_totals or not category_totals:
        print("No data available to show graphs.")
        return
    weeks=weekly_totals.keys()
    weekly_amount=weekly_totals.values()

    plt.figure(figsize=(10,6))
    plt.bar(weeks,weekly_amount)
    plt.title("Weekly Spending")
    plt.xlabel("Week")
    plt.ylabel("Amount spent")
    plt.show()

#------CATEGORY PIE CHART------
    labels=category_totals.keys()
    values=category_totals.values()
    if values:
      explode=[0.1 if v==max(values)else 0 for v in values]
    else:
        explode=[]
    plt.figure(figsize=(6,4))
    plt.pie(values,
        labels=labels,
        autopct="%1.1f%%",
        explode=explode,
        startangle=90,
        shadow=True)
    plt.title("Spending Distribution by Category")
    plt.axis("equal")
    plt.show()
    
    
def main():

    profile = load_user_profile()

    if profile is None:
        print("\nFirst time setup")

        salary = get_salary()
        fixed_expenses = get_fixed_expenses()

        profile = {
            "salary": salary,
            "fixed_expenses": fixed_expenses
        }

        save_user_profile(profile)

    else:
        print("\nWelcome back! Loading saved profile")

        salary = profile["salary"]
        fixed_expenses = profile["fixed_expenses"]

    remaining_money, limit = set_spending_limit(profile)

    # variables to reuse later
    weekly_totals=load_weekly_data()
    total_spend=sum(weekly_totals.values())
    category_totals=load_category_data()
    
    print("DEBUG:",weekly_totals,category_totals)
    savings = None
    goals = load_goals()

    while True:

        print("\n===== PERSONAL FINANCE TRACKER =====")
        print("1 Track Weekly Expenses")
        print("2 Show Summary")
        print("3 Manage Goals")
        print("4 What-If Simulator")
        print("5 Financial Advisor")
        print("6 Spending Prediction")
        print("7 Show Graphs")
        print("8 Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            new_total_spend,new_categories,new_weeks,new_weekly_totals=track_weekly_expenses(limit,total_spend)
            total_spend=new_total_spend
            
            for cat,amt in new_categories.items():
                if cat in category_totals:
                    category_totals[cat]+=amt
                else:
                    category_totals[cat]=amt
                    
            weekly_totals.update(new_weekly_totals)
            
            save_weekly_data(new_weeks)
        elif choice == "2":
            
            if not category_totals:
                print("NO expenses data found.Track weekly expenses first.")
            else:
             savings = show_summary(category_totals, total_spend, remaining_money)
             save_month_data(total_spend, savings)
            

        elif choice == "3":
            show_goals(goals)
            goals = add_goal(goals)
            save_goals(goals)
            estimate_goal_time(goals, savings,remaining_money,total_spend)

        elif choice == "4":
            what_if_simulator(goals, savings)

        elif choice == "5":
            financial_advisor(category_totals, savings)

        elif choice == "6":
            spending_prediction(remaining_money)

        elif choice == "7":
            show_graphs(weekly_totals, category_totals)

        elif choice == "8":
            print("Exiting program. Goodbye!")
            break

        else:
            print("Invalid choice. Try again.")
       
if __name__=="__main__":
     main()