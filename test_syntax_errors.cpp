/*
 * 测试脚本 - 包含多种C++语法错误用于AI代码审核
 * Test script with various C++ syntax errors for AI code review
 */

#include <iostream>
#include <vector>
#include <string>
#include <map>
// 缺少必要的头文件
// #include <algorithm>
// #include <memory>

using namespace std;

// 1. 类声明中的语法错误
class URLProcessor {
private:
    vector<string> urls;
    map<string, string> config;
    
public:
    // 2. 构造函数缺少初始化列表分号
    URLProcessor(const string& configFile) 
        : urls()
        config()  // 缺少逗号
    {
        loadConfig(configFile);
    }
    
    // 3. 函数声明缺少返回类型
    validateURL(const string& url) {
        // 4. 未声明的变量使用
        regex urlPattern("^https?://[^\\s/$.?#].[^\\s]*$");
        return regex_match(url, urlPattern);
    }
    
    // 5. 函数参数类型错误
    void addURL(string url) {  // 应该是const string&
        if (validateURL(url)) {
            urls.push_back(url);
        }
        // 6. 缺少else分支可能导致逻辑错误
    }
    
    // 7. 返回类型与实际返回值不匹配
    int getURLCount() {
        return urls;  // 应该返回urls.size()
    }
    
    // 8. 内存泄漏 - new但没有delete
    char* processURL(const string& url) {
        char* result = new char[256];
        strcpy(result, url.c_str());  // 缺少#include <cstring>
        return result;  // 调用者需要delete，但没有文档说明
    }
    
private:
    // 9. 函数实现缺少返回语句
    bool loadConfig(const string& filename) {
        ifstream file(filename);  // 缺少#include <fstream>
        if (!file.is_open()) {
            cout << "Failed to open config file" << endl;
            // 缺少return false;
        }
        
        string line;
        while (getline(file, line)) {
            // 10. 数组越界风险
            size_t pos = line.find('=');
            string key = line.substr(0, pos);
            string value = line.substr(pos + 1);  // 如果pos是npos会出错
            config[key] = value;
        }
        // 函数应该返回bool但缺少return语句
    }
};

// 11. 全局函数参数传递效率问题
void printURLs(vector<string> urls) {  // 应该传引用
    for (int i = 0; i <= urls.size(); i++) {  // 12. 循环条件错误，应该是<
        cout << urls[i] << endl;  // 可能数组越界
    }
}

// 13. 类定义后缺少分号
class HTTPClient {
    private:
        string baseURL;
    
    public:
        HTTPClient(const string& url) : baseURL(url) {}
        
        // 14. 纯虚函数语法错误
        virtual string sendRequest(const string& endpoint) = 0  // 缺少分号
        
        // 15. 析构函数应该是虚函数
        ~HTTPClient() {
            // 清理资源
        }
}  // 缺少分号

// 16. 模板语法错误
template<typename T
class Container {  // 缺少>
    private:
        T* data;
        size_t size;
    
    public:
        Container() : data(nullptr), size(0) {}
        
        // 17. 拷贝构造函数浅拷贝问题
        Container(const Container& other) {
            data = other.data;  // 浅拷贝，应该深拷贝
            size = other.size;
        }
        
        // 18. 缺少赋值操作符重载
        
        ~Container() {
            delete[] data;  // 如果data是用new分配的单个对象，应该用delete
        }
};

// 19. 主函数参数错误
int main(int argc, char argv[]) {  // 应该是char* argv[]
    
    // 20. 未初始化的指针
    URLProcessor* processor;
    processor->addURL("https://example.com");  // 使用未初始化的指针
    
    // 21. 数组声明语法错误
    int numbers[10;  // 缺少]
    
    // 22. switch语句缺少break
    int option = 1;
    switch (option) {
        case 1:
            cout << "Option 1 selected" << endl;
        case 2:  // 缺少break，会fall through
            cout << "Option 2 selected" << endl;
            break;
        default:
            cout << "Default option" << endl;
    }
    
    // 23. 字符串连接语法错误
    string message = "Hello" + " " + "World";  // 应该至少有一个是string类型
    
    // 24. 悬空指针
    int* ptr = new int(10);
    delete ptr;
    cout << *ptr << endl;  // 使用已删除的指针
    
    // 25. 循环变量作用域错误
    for (int i = 0; i < 10; i++) {
        int temp = i * 2;
    }
    cout << temp << endl;  // temp超出作用域
    
    // 26. 异常处理语法错误
    try {
        vector<int> vec(10);
        vec.at(20);  // 会抛出异常
    }
    catch (out_of_range e) {  // 应该是const out_of_range&
        cout << "Index out of range" << endl;
    }
    
    // 27. 函数调用参数不匹配
    printURLs();  // 缺少参数
    
    // 28. 返回语句缺少值
    return;  // main函数应该返回int
}

// 29. 函数定义与声明不匹配
void printURLs(const vector<string>& urls) {  // 声明和定义参数类型不一致
    for (const auto& url : urls) {
        cout << url << endl;
    }
}

/* 30. 未关闭的注释块
   这个脚本包含以下C++语法错误类型：
   - 缺少头文件包含
   - 构造函数初始化列表语法错误
   - 函数声明缺少返回类型
   - 未声明变量使用
   - 内存管理错误
   - 数组越界
   - 循环条件错误
   - 类定义缺少分号
   - 模板语法错误
   - 拷贝构造函数浅拷贝
   - 悬空指针
   - 异常处理语法错误
   - 函数参数不匹配
   - 作用域错误
   - switch case缺少break