import http from "k6/http";
import { check, sleep } from "k6";

// Test configuration
export const options = {
  thresholds: {
    // Assert that 98% of requests finish within 3000ms.
    http_req_duration: ["p(98) < 3000"],
  },
  // Ramp the number of virtual users up and down
  stages: [
    { duration: "30s", target: 15 },
    { duration: "1m", target: 15 },
    { duration: "20s", target: 0 },
  ],
};

// simulate user behavior
export default function () {
  let res = http.get("http://localhost:80/"); // correct URL to localhost
  // check response status
  check(res, { "status was 200": (r) => r.status == 200 });
  sleep(1);
}