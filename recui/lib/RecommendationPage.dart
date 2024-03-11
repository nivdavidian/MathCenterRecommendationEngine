// ignore_for_file: sized_box_for_whitespace

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:recui/HomePage.dart';
import 'dart:convert';
import 'package:url_launcher/url_launcher.dart';

class RecommendationPage extends StatefulWidget {
  const RecommendationPage({super.key, required this.data});

  final Map<String, String> data;
  @override
  State<RecommendationPage> createState() => _RecommendationPageState();
}

class _RecommendationPageState extends State<RecommendationPage> {
  bool isLoading = true;
  dynamic recommendations;

  Future<void> redirectToUrl(String worksheetUid) async {
    final String worksheetUriString =
        "https://math-center.org/he-IL/worksheet/$worksheetUid/%D7%97%D7%99%D7%91%D7%95%D7%A8-%D7%95%D7%97%D7%99%D7%A1%D7%95%D7%A8-%D7%A2%D7%93-10-%D7%93%D7%A3-%D7%9E%D7%A1%D7%A4%D7%A8-1/";
    final String interactiveUriString =
        "https://math-center.org/he-IL/worksheet/$worksheetUid/interactive/";
    final Uri worksheetUri = Uri.parse(worksheetUriString);
    if (!await launchUrl(worksheetUri)) {
      final Uri interactiveUri = Uri.parse(interactiveUriString);
      if (!await launchUrl(interactiveUri)) {
        print("something went wrong not interactive and not worksheet");
      }
    }
  }

  Future<void> recommend(String worksheetUid) async {
    var url = Uri.parse(
        'http://13.49.248.115:3000/getrecommendation?worksheet_uid=$worksheetUid');
    var response = await http.get(url);

    if (response.statusCode == 200) {
      // If the server returns a 200 OK response, then parse the JSON.
      var data = json.decode(response.body);
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
                    (index) => MyBorderButton(data: [
                      recommendations[index]["worksheet_uid"],
                      recommendations[index]["worksheet_name"],
                    ], width: 400, height: 55, onTap: redirectToUrl),
                  ),
                ],
              ),
            ),
    );
  }
}
