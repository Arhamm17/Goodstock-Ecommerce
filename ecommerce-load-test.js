import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = "http://184.193.177.24:30080";

export const options = {
  stages: [
    {
      duration: "2m",
      target: 100
    },
    {
      duration: "5m",
      target: 300
    },
    {
      duration: "3m",
      target: 500
    },
    {
      duration: "2m",
      target: 0
    }
  ],
};

export default function () {

  let products = http.get(
    `${BASE_URL}/products`
  );

  check(products, {
    "products 200": (r) => r.status === 200,
  });


  let orders = http.get(
    `${BASE_URL}/orders`
  );

  check(orders, {
    "orders 200": (r) => r.status === 200,
  });


  sleep(1);
}