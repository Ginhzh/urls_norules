/*
 * 正确的C++测试脚本 - 用于AI代码审核评估
 * Correct C++ test script for AI code review evaluation
 * 实现URL短链接服务的完整功能测试
 */

#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <regex>
#include <memory>
#include <fstream>
#include <algorithm>
#include <chrono>
#include <random>
#include <stdexcept>
#include <sstream>

class URLValidator {
private:
    std::regex urlPattern;

public:
    URLValidator() : urlPattern(
        R"(^https?://(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:/?|[/?]\S+)$)",
        std::regex_constants::icase) {}

    bool isValidURL(const std::string& url) const {
        if (url.empty()) {
            return false;
        }
        return std::regex_match(url, urlPattern);
    }

    std::string sanitizeURL(const std::string& url) const {
        std::string cleaned = url;
        
        // 移除首尾空格
        cleaned.erase(0, cleaned.find_first_not_of(" \t\n\r"));
        cleaned.erase(cleaned.find_last_not_of(" \t\n\r") + 1);
        
        // 确保有协议前缀
        if (cleaned.find("http://") != 0 && cleaned.find("https://") != 0) {
            cleaned = "https://" + cleaned;
        }
        
        return cleaned;
    }
};

struct URLRecord {
    std::string id;
    std::string originalURL;
    std::string shortURL;
    std::chrono::system_clock::time_point createdAt;
    std::chrono::system_clock::time_point expiresAt;
    int clickCount;
    bool isActive;

    URLRecord() : clickCount(0), isActive(true) {
        createdAt = std::chrono::system_clock::now();
        expiresAt = std::chrono::system_clock::time_point::max();
    }
};

struct URLStats {
    int totalClicks;
    std::set<std::string> uniqueVisitors;
    std::chrono::system_clock::time_point lastAccessed;

    URLStats() : totalClicks(0) {}
};

class URLProcessor {
private:
    std::unique_ptr<URLValidator> validator;
    std::map<std::string, std::string> config;
    std::string baseURL;
    std::map<std::string, URLRecord> urlsDB;
    std::map<std::string, URLStats> statsDB;
    
    std::random_device randomDevice;
    std::mt19937 generator;
    std::uniform_int_distribution<> distribution;

public:
    explicit URLProcessor(const std::string& configFile = "") 
        : validator(std::make_unique<URLValidator>()),
          baseURL("https://short.ly"),
          generator(randomDevice()),
          distribution(0, 61) {
        
        if (!configFile.empty()) {
            loadConfig(configFile);
        }
    }

    // 拷贝构造函数
    URLProcessor(const URLProcessor& other) 
        : validator(std::make_unique<URLValidator>(*other.validator)),
          config(other.config),
          baseURL(other.baseURL),
          urlsDB(other.urlsDB),
          statsDB(other.statsDB),
          generator(randomDevice()),
          distribution(0, 61) {}

    // 赋值操作符
    URLProcessor& operator=(const URLProcessor& other) {
        if (this != &other) {
            validator = std::make_unique<URLValidator>(*other.validator);
            config = other.config;
            baseURL = other.baseURL;
            urlsDB = other.urlsDB;
            statsDB = other.statsDB;
        }
        return *this;
    }

    // 移动构造函数
    URLProcessor(URLProcessor&& other) noexcept 
        : validator(std::move(other.validator)),
          config(std::move(other.config)),
          baseURL(std::move(other.baseURL)),
          urlsDB(std::move(other.urlsDB)),
          statsDB(std::move(other.statsDB)),
          generator(randomDevice()),
          distribution(0, 61) {}

    // 移动赋值操作符
    URLProcessor& operator=(URLProcessor&& other) noexcept {
        if (this != &other) {
            validator = std::move(other.validator);
            config = std::move(other.config);
            baseURL = std::move(other.baseURL);
            urlsDB = std::move(other.urlsDB);
            statsDB = std::move(other.statsDB);
        }
        return *this;
    }

    virtual ~URLProcessor() = default;

private:
    bool loadConfig(const std::string& filename) {
        std::ifstream file(filename);
        if (!file.is_open()) {
            std::cerr << "Warning: Failed to open config file: " << filename << std::endl;
            return false;
        }

        std::string line;
        while (std::getline(file, line)) {
            size_t pos = line.find('=');
            if (pos != std::string::npos) {
                std::string key = line.substr(0, pos);
                std::string value = line.substr(pos + 1);
                
                // 移除空格
                key.erase(0, key.find_first_not_of(" \t"));
                key.erase(key.find_last_not_of(" \t") + 1);
                value.erase(0, value.find_first_not_of(" \t"));
                value.erase(value.find_last_not_of(" \t") + 1);
                
                config[key] = value;
            }
        }
        
        // 更新baseURL如果配置中有定义
        auto it = config.find("base_url");
        if (it != config.end()) {
            baseURL = it->second;
        }
        
        return true;
    }

    std::string generateShortID(int length = 6) {
        const std::string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        std::string result;
        result.reserve(length);
        
        for (int i = 0; i < length; ++i) {
            result += chars[distribution(generator)];
        }
        
        return result;
    }

public:
    URLRecord createShortURL(const std::string& originalURL, 
                            const std::string& customAlias = "",
                            const std::chrono::system_clock::time_point& expiresAt = std::chrono::system_clock::time_point::max()) {
        
        // 验证原始URL
        if (!validator->isValidURL(originalURL)) {
            throw std::invalid_argument("Invalid URL: " + originalURL);
        }

        // 清理URL
        std::string cleanedURL = validator->sanitizeURL(originalURL);

        std::string shortID;
        
        // 生成或使用自定义别名
        if (!customAlias.empty()) {
            if (urlsDB.find(customAlias) != urlsDB.end()) {
                throw std::runtime_error("Alias already exists: " + customAlias);
            }
            shortID = customAlias;
        } else {
            // 生成唯一的短ID
            do {
                shortID = generateShortID();
            } while (urlsDB.find(shortID) != urlsDB.end());
        }

        // 创建URL记录
        URLRecord record;
        record.id = shortID;
        record.originalURL = cleanedURL;
        record.shortURL = baseURL + "/" + shortID;
        record.createdAt = std::chrono::system_clock::now();
        record.expiresAt = expiresAt;
        record.clickCount = 0;
        record.isActive = true;

        // 存储记录
        urlsDB[shortID] = record;
        statsDB[shortID] = URLStats();

        return record;
    }

    std::string getOriginalURL(const std::string& shortID) {
        auto it = urlsDB.find(shortID);
        if (it == urlsDB.end()) {
            throw std::runtime_error("Short URL not found: " + shortID);
        }

        URLRecord& record = it->second;

        // 检查是否过期
        auto now = std::chrono::system_clock::now();
        if (record.expiresAt != std::chrono::system_clock::time_point::max() && now > record.expiresAt) {
            throw std::runtime_error("Short URL has expired: " + shortID);
        }

        // 检查是否激活
        if (!record.isActive) {
            throw std::runtime_error("Short URL is inactive: " + shortID);
        }

        // 更新统计信息
        updateStats(shortID, "127.0.0.1");

        return record.originalURL;
    }

    void updateStats(const std::string& shortID, const std::string& visitorIP = "127.0.0.1") {
        auto urlIt = urlsDB.find(shortID);
        auto statsIt = statsDB.find(shortID);
        
        if (urlIt != urlsDB.end()) {
            urlIt->second.clickCount++;
        }
        
        if (statsIt != statsDB.end()) {
            statsIt->second.totalClicks++;
            statsIt->second.uniqueVisitors.insert(visitorIP);
            statsIt->second.lastAccessed = std::chrono::system_clock::now();
        }
    }

    URLRecord getURLStats(const std::string& shortID) const {
        auto it = urlsDB.find(shortID);
        if (it == urlsDB.end()) {
            throw std::runtime_error("Short URL not found: " + shortID);
        }
        return it->second;
    }

    std::vector<std::map<std::string, std::string>> batchProcessURLs(const std::vector<std::string>& urls) {
        std::vector<std::map<std::string, std::string>> results;
        results.reserve(urls.size());

        for (const auto& url : urls) {
            std::map<std::string, std::string> result;
            result["original_url"] = url;

            try {
                if (validator->isValidURL(url)) {
                    URLRecord record = createShortURL(url);
                    result["status"] = "success";
                    result["short_url"] = record.shortURL;
                    result["short_id"] = record.id;
                } else {
                    result["status"] = "error";
                    result["error"] = "Invalid URL format";
                }
            } catch (const std::exception& e) {
                result["status"] = "error";
                result["error"] = e.what();
            }

            results.push_back(std::move(result));
        }

        return results;
    }

    int cleanupExpiredURLs() {
        auto now = std::chrono::system_clock::now();
        std::vector<std::string> expiredIDs;

        for (const auto& pair : urlsDB) {
            const URLRecord& record = pair.second;
            if (record.expiresAt != std::chrono::system_clock::time_point::max() && now > record.expiresAt) {
                expiredIDs.push_back(pair.first);
            }
        }

        // 删除过期的URL
        for (const auto& id : expiredIDs) {
            urlsDB.erase(id);
            statsDB.erase(id);
        }

        return static_cast<int>(expiredIDs.size());
    }

    size_t getURLCount() const {
        return urlsDB.size();
    }

    void printAllURLs() const {
        std::cout << "=== 所有短链接 ===" << std::endl;
        for (const auto& pair : urlsDB) {
            const URLRecord& record = pair.second;
            std::cout << "ID: " << record.id << " | " 
                      << record.originalURL << " -> " << record.shortURL 
                      << " (点击: " << record.clickCount << ")" << std::endl;
        }
    }
};

// 测试函数
void testURLProcessor() {
    std::cout << "=== URL处理器测试 ===" << std::endl;
    
    URLProcessor processor;

    // 测试URL列表
    std::vector<std::string> testUrls = {
        "https://www.google.com",
        "https://github.com/microsoft/vscode",
        "http://example.com/path/to/resource",
        "https://httpbin.org/json",
        "invalid-url",  // 无效URL
        "ftp://example.com/file",  // 不支持的协议
        "https://jsonplaceholder.typicode.com/posts/1"
    };

    // 批量处理测试
    auto results = processor.batchProcessURLs(testUrls);
    for (const auto& result : results) {
        const std::string& status = result.at("status");
        const std::string& url = result.at("original_url");

        if (status == "success") {
            const std::string& shortUrl = result.at("short_url");
            std::cout << "✓ " << url << " -> " << shortUrl << std::endl;
        } else {
            const std::string& error = result.at("error");
            std::cout << "✗ " << url << ": " << error << std::endl;
        }
    }

    // 测试短链接重定向
    std::cout << "\n=== 重定向测试 ===" << std::endl;
    
    int successCount = 0;
    for (const auto& result : results) {
        if (result.at("status") == "success" && successCount < 3) {
            const std::string& shortId = result.at("short_id");
            try {
                std::string originalUrl = processor.getOriginalURL(shortId);
                std::cout << "✓ " << shortId << " -> " << originalUrl << std::endl;
                successCount++;
            } catch (const std::exception& e) {
                std::cout << "✗ " << shortId << ": " << e.what() << std::endl;
            }
        }
    }

    // 测试统计功能
    std::cout << "\n=== 统计信息测试 ===" << std::endl;
    successCount = 0;
    for (const auto& result : results) {
        if (result.at("status") == "success" && successCount < 2) {
            const std::string& shortId = result.at("short_id");
            try {
                URLRecord stats = processor.getURLStats(shortId);
                std::cout << "ID: " << stats.id << std::endl;
                std::cout << "  点击次数: " << stats.clickCount << std::endl;
                std::cout << "  是否激活: " << (stats.isActive ? "是" : "否") << std::endl;
                successCount++;
            } catch (const std::exception& e) {
                std::cout << "✗ 获取统计失败 " << shortId << ": " << e.what() << std::endl;
            }
        }
    }

    // 测试过期URL清理
    std::cout << "\n=== 过期URL清理测试 ===" << std::endl;
    try {
        // 创建一个即将过期的URL
        auto expireTime = std::chrono::system_clock::now() + std::chrono::seconds(1);
        URLRecord expiredUrl = processor.createShortURL("https://example.com/expire-test", "", expireTime);
        std::cout << "创建即将过期的URL: " << expiredUrl.shortURL << std::endl;

        // 等待过期
        std::this_thread::sleep_for(std::chrono::seconds(2));

        // 清理过期URL
        int cleanedCount = processor.cleanupExpiredURLs();
        std::cout << "清理了 " << cleanedCount << " 个过期URL" << std::endl;

    } catch (const std::exception& e) {
        std::cout << "过期URL测试失败: " << e.what() << std::endl;
    }

    std::cout << "\n总URL数量: " << processor.getURLCount() << std::endl;
}

int main(int argc, char* argv[]) {
    std::cout << "URL短链接服务C++测试程序" << std::endl;
    std::cout << "======================================" << std::endl;

    try {
        testURLProcessor();
        std::cout << "\n======================================" << std::endl;
        std::cout << "所有测试完成！" << std::endl;
        return 0;

    } catch (const std::exception& e) {
        std::cerr << "测试过程中发生错误: " << e.what() << std::endl;
        return 1;
    } catch (...) {
        std::cerr << "发生未知错误！" << std::endl;
        return 2;
    }
}