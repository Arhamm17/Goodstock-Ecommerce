import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    {
      duration: "2m",
      target: 100
    },
    {
      duration: "3m",
      target: 250
    },
    {
      duration: "5m",
      target: 500
    },
    {
      duration: "2m",
      target: 0
    }
  ],
};

export default function () {

  const response = http.get(
    "http://184.193.177.24:30080/health"
  );

  check(response, {
    "status is 200": (r) => r.status === 200,
  });

  sleep(1);
}