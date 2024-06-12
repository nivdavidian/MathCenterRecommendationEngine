// ignore_for_file: sized_box_for_whitespace
import 'package:flutter/material.dart';
import 'package:recui/ChooseAlg.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  String _username = "";
  String _password = "";

  String _error_message = "";
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Login Page"),
        // actions: [
        //   IconButton(onPressed: () {}, icon: const Icon(Icons.favorite))
        // ],
        backgroundColor: Colors.blue[50],
      ),
      body: Column(
        children: [
          const Spacer(),
          const Center(
            child: Text(
              "Login",
              style: TextStyle(fontSize: 20),
            ),
          ),
          Container(
            width: 300,
            height: 50,
            child: Padding(
              padding: const EdgeInsets.all(8.0),
              child: TextField(
                controller: _usernameController,
                decoration: const InputDecoration(
                  hintText: "Username",
                ),
                onChanged: (value) {
                  _username = value;
                },
              ),
            ),
          ),
          Container(
            width: 300,
            height: 50,
            child: Padding(
              padding: const EdgeInsets.all(8.0),
              child: TextField(
                controller: _passwordController,
                obscureText: true,
                decoration: const InputDecoration(
                  hintText: "Password",
                ),
                onChanged: (value) {
                  _password = value;
                },
              ),
            ),
          ),
          Center(
            child: TextButton(
              child: const Text("Login"),
              onPressed: () {
                if (_username == "niv" && _password == "123") {
                  Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const ChooseAlg()),
    );
                }
                else{
                  setState(() {
                    _error_message = "Wrong Auth info";
                  });
                }
                  
              },
            ),
          ),
          _error_message == ""
              ? const SizedBox.shrink()
              : Text(
                  _error_message,
                  style: const TextStyle(color: Colors.red),
                ),
          const Spacer(),
        ],
      ),
    );
  }
}
