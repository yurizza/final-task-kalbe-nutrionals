--Retrieve all records from the "customer" table
select *  from customer c  

--update the "new_income" column by converting the "income" column
UPDATE customer  SET new_income  = CAST(REPLACE(income , ',', '.') AS float);

--Determine the average age based on marital status
select "Marital Status", 
	AVG(age) AS average_age
from customer
group by 1;

--Determine the average age based on gender
select gender,
	avg(age) as average_age
from customer c  
group by 1;

--Find the store name with the highest total quantity of transactions
select t.storeid, s.storename, s.groupstore, 
	sum(qty) as total_quantity 
from store s 
join "transaction" t 
on t.storeid = s.storeid
group by 1, 2, 3
order by 2 desc 
limit 1;

-- Determine the best-selling product name with the highest total sales amount
select "Product Name" , 
	sum(totalamount) as  total_amount
from product p 
join "transaction" t 
on t.productid = p.productid 
group by 1
order by 2 desc 
limit 1;
