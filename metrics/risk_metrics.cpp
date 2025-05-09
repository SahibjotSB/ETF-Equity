#include <cmath>
#include <vector>
#include <algorithm>

extern "C" {

double calculate_sharpe(const double* returns, int size, double risk_free_rate) {
    double sum = 0;
    for (int i = 0; i < size; ++i) sum += returns[i];
    double mean = sum / size;

    double variance = 0;
    for (int i = 0; i < size; ++i) variance += std::pow(returns[i] - mean, 2);
    double std_dev = std::sqrt(variance / size);

    return ((mean - risk_free_rate) / std_dev) * std::sqrt(252.0);
}

double calculate_volatility(const double* returns, int size) {
    double sum = 0;
    for (int i = 0; i < size; ++i) sum += returns[i];
    double mean = sum / size;

    double variance = 0;
    for (int i = 0; i < size; ++i) variance += std::pow(returns[i] - mean, 2);
    double std_dev = std::sqrt(variance / size);

    return std_dev * std::sqrt(252.0) * 100.0;
}

double calculate_max_drawdown(const double* returns, int size) {
    std::vector<double> cumulative(size);
    cumulative[0] = 1 + returns[0];

    for (int i = 1; i < size; ++i) {
        cumulative[i] = cumulative[i - 1] * (1 + returns[i]);
    }

    double max_drawdown = 0.0;
    double peak = cumulative[0];

    for (int i = 1; i < size; ++i) {
        if (cumulative[i] > peak) peak = cumulative[i];
        double drawdown = (cumulative[i] - peak) / peak;
        if (drawdown < max_drawdown) max_drawdown = drawdown;
    }

    return max_drawdown * 100.0;
}

}
