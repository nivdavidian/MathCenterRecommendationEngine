// ignore_for_file: sized_box_for_whitespace
import 'dart:developer';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  bool isLoading = true;
  var _data = [];
  Map<String, dynamic> clCodes = {};
  String initialDropValue = "IL-he";

  @override
  void initState() {
    super.initState();
    // fetchData();
  }

  Future<void> searchPage(
      String searchString, String cCode, String lCode) async {
    print(searchString);
    print(cCode);
    print(lCode);

    setState(() {
      isLoading = true;
    });

    // sleep(Durations.long4);

    setState(() {
      isLoading = false;
    });

    // setState(() {
    //   isLoading = true;
    // });
    // var url = Uri.parse(
    //     'http://localhost:3000/getpages?term=$searchString&cCode=$cCode&lCode=$lCode');
    // var response = await http.get(url);

    // if (response.statusCode == 200) {
    //   // If the server returns a 200 OK response, then parse the JSON.
    //   var data = json.decode(response.body);
    //   setState(() {
    //     isLoading = false;
    //     _data = data;
    //   });
    // } else {
    //   // If the server did not return a 200 OK response,
    //   // then throw an exception.
    //   log("${response.statusCode}");
    // }
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
        title: const Text("User Similarity"),
      ),
      body: Row(
        children: [
          Expanded(
            child: Column(
              children: [
                // MySearchBar(searchFunc: searchPage),
                SearchBar(
                  hintText: "search",
                  leading:
                      IconButton(onPressed: () {}, icon: const Icon(Icons.search)),
                  onSubmitted: (s) {
                    print(s);
                  },
                ),
                isLoading
                    ? const Padding(
                        padding: EdgeInsets.all(8),
                        child: CircularProgressIndicator(),
                      )
                    : const Text("niv"),
              ],
            ),
          ),
          const VerticalDivider(color: Colors.black, thickness: 5, indent: 5, endIndent: 5,),
          const Expanded(child: Text("niv"))
        ],
      ),
    );
  }

  // @override
  // Widget build(BuildContext context) {
  //   return Scaffold(
  //     appBar: AppBar(
  //       title: const Text("Welcome"),
  //     ),
  //     body: Column(
  //       children: [
  //         isLoading
  //             ? const Padding(
  //                 padding: EdgeInsets.all(8),
  //                 child: CircularProgressIndicator(),
  //               )
  //             : Expanded(
  //                 child: SingleChildScrollView(
  //                   child: Column(
  //                       // crossAxisAlignment: CrossAxisAlignment.stretch,
  //                       children: [
  //                         ...List.generate(
  //                           _data.length,
  //                           (index) => Padding(
  //                             padding: const EdgeInsets.all(8.0),
  //                             child: Container(
  //                               width: 350,
  //                               height: 70,
  //                               decoration: BoxDecoration(
  //                                 border:
  //                                     Border.all(color: Colors.black, width: 1),
  //                                 borderRadius: BorderRadius.circular(20),
  //                               ),
  //                               child: InkWell(
  //                                 onTap: () {
  //                                   Navigator.push(
  //                                       context,
  //                                       MaterialPageRoute(
  //                                           builder: (context) =>
  //                                               RecommendationPage(
  //                                                 data: {
  //                                                   "worksheet_id": _data[index]
  //                                                           ["worksheet_id"]
  //                                                       .toString(),
  //                                                   "worksheet_name": _data[
  //                                                               index]
  //                                                           ["worksheet_name"]
  //                                                       .toString()
  //                                                 },
  //                                                 cCode: initialDropValue
  //                                                     .split("-")[0],
  //                                                 lCode: initialDropValue
  //                                                     .split("-")[1],
  //                                               )));
  //                                 },
  //                                 splashColor: Colors.purple[50],
  //                                 child: Column(
  //                                   children: [
  //                                     Text(_data[index]["worksheet_name"]),
  //                                     Text(_data[index]["worksheet_id"]),
  //                                   ],
  //                                 ),
  //                               ),
  //                             ),
  //                           ),
  //                         ),
  //                       ]),
  //                 ),
  //               ),
  //       ],
  //     ),
  //   );
  // }
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
