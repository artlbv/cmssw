"""Build a standalone copy of CMSSW's HGCalWaferMask::waferXY (the 8-argument overload) from this checkout.

The function body is copied verbatim from Geometry/HGCalCommonData/src/HGCalWaferMask.cc (debug logging removed)
and wrapped in a main() that reads 'part place waferSize offset v17' per line from stdin and prints
'part place v17 x0 y0 x1 y1 ...' (the sensitive-silicon outline of a partial wafer at the origin).
The executable is written to the work directory and reused.
"""
import os
import re
import subprocess

from paths import CMSSW_SRC, WORK

HELPER = os.path.join(WORK, "waferxy")
SIGNATURE = "std::vector<std::pair<double, double> > HGCalWaferMask::waferXY(const int& part,\n" \
            "                                                                const int& place,"

PRELUDE = """#include <iostream>
#include <sstream>
#include <string>
#include <utility>
#include <vector>
#include "Geometry/HGCalCommonData/interface/HGCalTypes.h"
static constexpr double sqrt3_ = 1.732050807568877;
static constexpr double sin_60_ = 0.5 * sqrt3_;
static constexpr double cos_60_ = 0.5;
static constexpr double offsetAir_ = 0.001;
static constexpr double tan_60_ = sqrt3_;
"""

MAIN = """
int main() {
  std::string line;
  while (std::getline(std::cin, line)) {
    std::istringstream is(line);
    int part, place, v17;
    double size, offset;
    if (!(is >> part >> place >> size >> offset >> v17))
      continue;
    auto xy = waferXY(part, place, size, offset, 0.0, 0.0, v17 > 0, false);
    std::cout << part << " " << place << " " << v17;
    for (auto& p : xy)
      std::cout << " " << p.first << " " << p.second;
    std::cout << "\\n";
  }
  return 0;
}
"""


def extract_function(src):
    start = src.index(SIGNATURE)
    i = src.index("{", start)
    depth = 0
    while True:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    body = re.sub(r"#ifdef EDM_ML_DEBUG.*?#endif", "", src[start:i + 1], flags=re.S)
    return body.replace("HGCalWaferMask::waferXY", "waferXY")


def ensure_helper():
    if os.path.exists(HELPER):
        return HELPER
    src = open(os.path.join(CMSSW_SRC, "Geometry/HGCalCommonData/src/HGCalWaferMask.cc")).read()
    os.makedirs(WORK, exist_ok=True)
    with open(HELPER + ".cc", "w") as f:
        f.write(PRELUDE + extract_function(src) + MAIN)
    cxx = os.environ.get("CXX", "g++")
    subprocess.run([cxx, "-O2", "-std=c++17", "-I", CMSSW_SRC, "-o", HELPER, HELPER + ".cc"], check=True)
    return HELPER


if __name__ == "__main__":
    print(ensure_helper())
