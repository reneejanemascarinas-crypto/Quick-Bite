from flask import Flask, render_template, request, redirect, url_for
from collections import deque

app = Flask(__name__)

# Queue for pending customer orders
order_queue = deque()

# List for completed orders
order_history = []

# Stores the most recently processed order
processed_order = None

# Queue number counter
next_queue_number = 1


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# VIEW ORDER QUEUE
@app.route("/queue")
def view_queue():
    return render_template(
        "queue.html",
        orders=list(order_queue),
        processed=processed_order,
        history=order_history
    )


# PROCESS THE FIRST PENDING ORDER (FIFO)
@app.route("/process-order", methods=["POST"])
def process_order():
    global processed_order

    if order_queue:
        processed_order = order_queue.popleft()
        processed_order["status"] = "Completed"
        order_history.append(processed_order)
    else:
        processed_order = None

    return redirect(url_for("view_queue"))


# UPDATE ORDER STATUS
@app.route("/update-status/<int:queue_number>", methods=["POST"])
def update_status(queue_number):
    global processed_order

    new_status = request.form.get("status", "").strip()

    allowed_statuses = ["Pending", "Preparing", "Completed"]

    if new_status not in allowed_statuses:
        return redirect(url_for("view_queue"))

    for order in order_queue:
        if order["queue_number"] == queue_number:

            order["status"] = new_status

            # Move completed order to order history
            if new_status == "Completed":
                order_queue.remove(order)
                order_history.append(order)
                processed_order = order

            break

    return redirect(url_for("view_queue"))


# DELETE A COMPLETED ORDER FROM HISTORY
@app.route("/delete-order/<int:queue_number>", methods=["POST"])
def delete_order(queue_number):
    global processed_order

    order_history[:] = [
        order for order in order_history
        if order["queue_number"] != queue_number
    ]

    if (
        processed_order is not None
        and processed_order["queue_number"] == queue_number
    ):
        processed_order = None

    return redirect(url_for("view_queue"))


# DELETE A PENDING ORDER FROM QUEUE
@app.route("/delete-pending-order/<int:queue_number>", methods=["POST"])
def delete_pending_order(queue_number):
    for order in order_queue:
        if order["queue_number"] == queue_number:
            order_queue.remove(order)
            break

    return redirect(url_for("view_queue"))


# OPEN EDIT ORDER PAGE
@app.route("/edit-order/<int:queue_number>")
def edit_order(queue_number):
    customer_order = None

    for order in order_queue:
        if order["queue_number"] == queue_number:
            customer_order = order
            break

    if customer_order is None:
        return redirect(url_for("view_queue"))

    return render_template(
        "edit_order.html",
        customer=customer_order
    )


# SAVE UPDATED ORDER
@app.route("/update-order/<int:queue_number>", methods=["POST"])
def update_order(queue_number):
    for order in order_queue:
        if order["queue_number"] == queue_number:

            order["name"] = request.form.get("name", "").strip()
            order["contact"] = request.form.get("contact", "").strip()
            order["address"] = request.form.get("address", "").strip()
            order["order"] = request.form.get("order", "").strip()
            order["total"] = request.form.get("total", "").strip()

            break

    return redirect(url_for("view_queue"))


# PLACE A NEW CUSTOMER ORDER
@app.route("/place-order", methods=["POST"])
def place_order():
    global next_queue_number

    name = request.form.get("name", "").strip()
    contact = request.form.get("contact", "").strip()
    address = request.form.get("address", "").strip()
    order = request.form.get("order", "").strip()
    total = request.form.get("total", "").strip()

    customer_order = {
        "queue_number": next_queue_number,
        "name": name,
        "contact": contact,
        "address": address,
        "order": order,
        "total": total,
        "status": "Pending"
    }

    order_queue.append(customer_order)
    next_queue_number += 1

    return render_template(
        "confirmation.html",
        name=name,
        contact=contact,
        address=address,
        order=order,
        total=total,
        queue_number=customer_order["queue_number"]
    )


# RUN THE APPLICATION
if __name__ == "__main__":
    app.run(debug=True)