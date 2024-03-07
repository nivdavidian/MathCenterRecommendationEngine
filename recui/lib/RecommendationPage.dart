// ignore_for_file: sized_box_for_whitespace

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class RecommendationPage extends StatefulWidget {
  const RecommendationPage({super.key, required this.data});

  final Map<String, String> data;
  @override
  State<RecommendationPage> createState() => _RecommendationPageState();
}

class _RecommendationPageState extends State<RecommendationPage> {
  bool isLoading = true;
  dynamic recommendations;

  Future<void> recommend(String worksheetUid) async {
    var url = Uri.parse(
        'http://127.0.0.1:5000/getrecommendation?worksheet_uid=$worksheetUid');
    var response = await http.get(url);

    if (response.statusCode == 200) {
      // If the server returns a 200 OK response, then parse the JSON.
      var data = json.decode(response.body);
      print(data);
      setState(() {
        isLoading = false;
        recommendations = data;
      });
    } else {
      // If the server did not return a 200 OK response,
      // then throw an exception.
      print("failed");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: SelectableText(
            "Recommendations for ${widget.data["worksheet_id"]} (${widget.data["worksheet_name"]})"),
      ),
      body: isLoading
          ? () {
              recommend(widget.data["worksheet_id"] ?? "");
              return const CircularProgressIndicator();
            }()
          : SingleChildScrollView(
              child: Column(
                children: [
                  ...List.generate(
                    recommendations.length,
                    (index) => Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Center(
                        child: Container(
                          width: 300,
                          height: 50,
                          child: SelectableText(
                              '${recommendations[index]["worksheet_name"]} (${recommendations[index]["worksheet_uid"]})'),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
