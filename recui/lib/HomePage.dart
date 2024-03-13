// ignore_for_file: sized_box_for_whitespace
import 'dart:developer';
import 'dart:html';

import 'package:flutter/material.dart';
import 'package:recui/RecommendationPage.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final _searchController = TextEditingController();
  bool isLoading = true;

  String _searchString = "";
  var _data = [];
  Map<String, dynamic> clCodes = {};
  String initial_drop_value = "IL-he";

  @override
  void initState() {
    super.initState();
    fetchData();
    getCLcodes();
  }

  Future<void> getCLcodes() async {
    var url = Uri.parse('http://localhost:3000/getclcodes');
    var response = await http.get(url);

    if (response.statusCode == 200) {
      // If the server returns a 200 OK response, then parse the JSON.
      var data = json.decode(response.body);
      setState(() {
        clCodes = data;
      });
    } else {
      // If the server did not return a 200 OK response,
      // then throw an exception.
      log("${response.statusCode}");
    }
  }

  Future<void> searchPage(String searchString) async {
    setState(() {
      isLoading = true;
    });
    var split = initial_drop_value.split("-");
    var cCode = split[0];
    var lCode = split[1];
    var url = Uri.parse(
        'http://localhost:3000/getpages?term=$searchString&cCode=$cCode&lCode=$lCode');
    var response = await http.get(url);

    if (response.statusCode == 200) {
      // If the server returns a 200 OK response, then parse the JSON.
      var data = json.decode(response.body);
      setState(() {
        isLoading = false;
        _data = data;
      });
    } else {
      // If the server did not return a 200 OK response,
      // then throw an exception.
      log("${response.statusCode}");
    }
  }

  Future<void> fetchData() async {
    var url = Uri.parse('http://localhost:3000/getpages');
    var response = await http.get(url);

    if (response.statusCode == 200) {
      // If the server returns a 200 OK response, then parse the JSON.
      var data = json.decode(response.body);
      setState(() {
        isLoading = false;
        _data = data;
      });
    } else {
      // If the server did not return a 200 OK response,
      // then throw an exception.
      log("${response.statusCode}");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Welcome"),
      ),
      body: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Center(
                child: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Container(
                    width: 355,
                    height: 50,
                    decoration: BoxDecoration(
                        border: Border.all(color: Colors.black, width: 1.0),
                        borderRadius: BorderRadius.circular(50)),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Container(
                          width: 300,
                          height: 50,
                          child: Padding(
                            padding: const EdgeInsets.fromLTRB(8, 0, 2, 0),
                            child: TextField(
                              controller: _searchController,
                              decoration: const InputDecoration(
                                  border: InputBorder.none),
                              onChanged: (value) {
                                _searchString = value;
                              },
                            ),
                          ),
                        ),
                        Padding(
                          padding: const EdgeInsets.fromLTRB(2, 0, 8, 0),
                          child: IconButton(
                            onPressed: () async {
                              searchPage(_searchString);
                            },
                            icon: const Icon(Icons.search),
                          ),
                        )
                      ],
                    ),
                  ),
                ),
              ),
              DropdownButton(
                  value: initial_drop_value,
                  items: () {
                    var cl = [];
                    for (var key in clCodes.keys) {
                      for (var value in clCodes[key]) {
                        cl.add('$key-$value');
                      }
                    }
                    return cl.map((e) => DropdownMenuItem(
                          value: e,
                          child: Text(e),
                        ));
                  }()
                      .toList(),
                  onChanged: (value) {
                    setState(() {
                      initial_drop_value = value.toString();
                    });
                    return;
                  })
            ],
          ),
          isLoading
              ? const Padding(
                  padding: EdgeInsets.all(8),
                  child: CircularProgressIndicator(),
                )
              : Expanded(
                  child: SingleChildScrollView(
                    child: Column(
                        // crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          ...List.generate(
                            _data.length,
                            (index) => Padding(
                              padding: const EdgeInsets.all(8.0),
                              child: Container(
                                width: 350,
                                height: 70,
                                decoration: BoxDecoration(
                                  border:
                                      Border.all(color: Colors.black, width: 1),
                                  borderRadius: BorderRadius.circular(20),
                                ),
                                child: InkWell(
                                  onTap: () {
                                    Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                            builder: (context) =>
                                                RecommendationPage(
                                                  data: {
                                                    "worksheet_id": _data[index]
                                                            ["worksheet_id"]
                                                        .toString(),
                                                    "worksheet_name": _data[
                                                                index]
                                                            ["worksheet_name"]
                                                        .toString()
                                                  },
                                                  cCode: initial_drop_value
                                                      .split("-")[0],
                                                  lCode: initial_drop_value
                                                      .split("-")[1],
                                                )));
                                  },
                                  splashColor: Colors.purple[50],
                                  child: Column(
                                    children: [
                                      Text(_data[index]["worksheet_name"]),
                                      Text(_data[index]["worksheet_id"]),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ]),
                  ),
                ),
        ],
      ),
    );
  }
}

class MyBorderButton extends StatelessWidget {
  final List<String> data;
  final double width;
  final double height;
  final Function onTap;
  const MyBorderButton(
      {super.key,
      required this.data,
      required this.width,
      required this.height,
      required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Container(
        width: width,
        height: height,
        decoration: BoxDecoration(
          border: Border.all(color: Colors.black, width: 1),
          borderRadius: BorderRadius.circular(20),
        ),
        child: InkWell(
          onTap: () {
            onTap(data[0]);
          },
          splashColor: Colors.purple[50],
          child: Column(
            children: [
              SelectableText(data[1].toString()),
              SelectableText(data[0].toString()),
            ],
          ),
        ),
      ),
    );
  }
}
