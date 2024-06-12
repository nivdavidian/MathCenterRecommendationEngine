import 'dart:convert';
import 'dart:developer';

import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'package:recui/json_classess.dart';

class UserSimilarityPage extends StatefulWidget {
  const UserSimilarityPage({super.key});

  @override
  State<UserSimilarityPage> createState() => _UserSimilarityPageState();
}

class _UserSimilarityPageState extends State<UserSimilarityPage> {
  var chosenHistory = List<MathCenterPage>.empty(growable: true);
  var pages = List<MathCenterPage>.empty(growable: true);

  var searchString = "";
  var cCode = "IL";
  var lCode = "he";

  var isLoading = false;

  @override
  void initState() {
    super.initState();
  }

  void updateChosenHistory(List<MathCenterPage> chosenHistory) {
    setState(() {
      chosenHistory = chosenHistory;
    });
  }

  void addChosen(MathCenterPage page) {
    setState(() {
      chosenHistory.add(page);
    });
  }

  void removeChosen(MathCenterPage page) {
    setState(() {
      chosenHistory.removeWhere((item) => item.uid == page.uid);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Similarity Page"),
      ),
      body: Stack(
        children: [
          Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    flex: 2,
                    child: SearchBar(
                      trailing: [
                        IconButton(
                          icon: const Icon(Icons.search),
                          onPressed: () {
                            searchPage(searchString, cCode, lCode);
                          },
                        )
                      ],
                      hintText: "Search Page",
                      elevation: MaterialStateProperty.all(10.0),
                      onChanged: (value) {
                        searchString = value;
                      },
                      onSubmitted: (value) {
                        searchPage(searchString, cCode, lCode);
                      },
                    ),
                  ),
                  const SizedBox(
                    width: 20,
                  ),
                  TextButton(
                      onPressed: () {
                        Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => HistoryPage(
                                  chosenHistory: chosenHistory,
                                  updateChosen: updateChosenHistory),
                            ));
                      },
                      child: const Text("History"))
                ],
              ),
              const SizedBox(
                height: 10,
              ),
              isLoading
                  ? const CircularProgressIndicator()
                  : Expanded(
                      child: ListView(
                        cacheExtent: 10,
                        addAutomaticKeepAlives: false,
                        children: List.generate(
                            pages.length,
                            (index) => PageTile(
                                  page: pages[index],
                                  addChosen: addChosen,
                                  removeChosen: removeChosen,
                                  selected: chosenHistory.any((element) =>
                                      element.uid == pages[index].uid),
                                )),
                      ),
                    ),
            ],
          ),
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: FittedBox(
              fit: BoxFit.scaleDown,
              child: TextButton(
                onPressed: () {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) =>
                              UserSimilarityRecommendationPage(
                                  chosenHistory: chosenHistory)));
                },
                style: ButtonStyle(
                  backgroundColor: MaterialStateProperty.all(Colors.pink[100]),
                  elevation: MaterialStateProperty.all(50.0),
                  shadowColor: MaterialStateProperty.all(Colors.black),
                  minimumSize: MaterialStateProperty.all(
                    const Size(150, 50),
                  ),
                ),
                child: const Text("Start Recommending"),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> searchPage(
      String searchString, String cCode, String lCode) async {
    setState(() {
      isLoading = true;
    });
    var url = Uri.parse(
        'http://127.0.0.1:5000/getpages?term=$searchString&cCode=$cCode&lCode=$lCode');
    var response = await http.get(url);
    if (response.statusCode == 200) {
      // If the server returns a 200 OK response, then parse the JSON.
      List<dynamic> data = json.decode(response.body);
      setState(() {
        isLoading = false;
        pages = data.map((e) => MathCenterPage.fromJson(e)).toList();
      });
    } else {
      // If the server did not return a 200 OK response,
      // then throw an exception.
      log("${response.statusCode}");
    }
  }
}

class PageTile extends StatefulWidget {
  const PageTile(
      {super.key,
      required this.page,
      required this.addChosen,
      required this.removeChosen,
      required this.selected});
  final MathCenterPage page;
  final Function addChosen;
  final Function removeChosen;
  final bool selected;

  @override
  State<PageTile> createState() => _PageTileState();
}

class _PageTileState extends State<PageTile> {
  @override
  Widget build(BuildContext context) {
    var page = widget.page;
    return Row(
      children: [
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(5.0),
            child: ListTile(
              selectedTileColor: Colors.pink[50],
              selected: widget.selected,
              title: Text(page.name),
              subtitle: Text(page.uid),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(7.0),
              ),
              // tileColor: Colors.amber,
              onTap: () {
                print(2);
              },
            ),
          ),
        ),
        IconButton(
            onPressed: () {
              widget.removeChosen(page);
            },
            icon: const Icon(Icons.remove)),
        IconButton(
            onPressed: () {
              widget.addChosen(page);
            },
            icon: const Icon(Icons.add))
      ],
    );
  }
}

class HistoryPage extends StatefulWidget {
  const HistoryPage(
      {super.key, required this.chosenHistory, required this.updateChosen});
  final List<MathCenterPage> chosenHistory;
  final Function updateChosen;

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("My History"),
      ),
      body: ListView(
        children: List.generate(
          widget.chosenHistory.length,
          (index) => ListTile(
            onTap: () {},
            title: Text(widget.chosenHistory[index].name),
            subtitle: Text(widget.chosenHistory[index].uid),
            trailing: IconButton(
              icon: const Icon(Icons.remove),
              onPressed: () {
                setState(() {
                  widget.chosenHistory.removeAt(index);
                });
                widget.updateChosen(widget.chosenHistory);
              },
            ),
          ),
        ),
      ),
    );
  }
}

class UserSimilarityRecommendationPage extends StatefulWidget {
  const UserSimilarityRecommendationPage(
      {super.key, required this.chosenHistory});

  final List<MathCenterPage> chosenHistory;

  @override
  State<UserSimilarityRecommendationPage> createState() =>
      _UserSimilarityRecommendationPageState();
}

class _UserSimilarityRecommendationPageState
    extends State<UserSimilarityRecommendationPage> {
  var isFolded = true;
  var recommendations = List<MathCenterPage>.empty(growable: true);
  var isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchRecommendations();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Recommedation - User Similarity"),
      ),
      body: isLoading
          ? const CircularProgressIndicator()
          : Column(
              children: [
                Row(
                  children: [
                    TextButton.icon(
                      onPressed: () {
                        setState(() {
                          isFolded = !isFolded;
                        });
                      },
                      icon: isFolded
                          ? const Icon(Icons.arrow_forward_ios)
                          : const Icon(Icons.arrow_back_ios),
                      label: const Text("History"),
                    ),
                    Expanded(
                      child: SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: Row(
                          children: isFolded
                              ? [const SizedBox()]
                              : List.generate(
                                  widget.chosenHistory.length,
                                  (index) => TextButton(
                                    onPressed: () {
                                      showModalBottomSheet(
                                      context: context,
                                      builder: (context) {
                                        return PageSheetInfo(
                                            page: widget.chosenHistory[index]);
                                      });
                                    },
                                    child:
                                        Text(widget.chosenHistory[index].name),
                                  ),
                                ),
                        ),
                      ),
                    )
                  ],
                ),
                Expanded(
                  child: ListView(
                    children: List.generate(
                        recommendations.length,
                        (index) => Padding(
                              padding: const EdgeInsets.all(5.0),
                              child: ListTile(
                                title: Text(recommendations[index].name),
                                subtitle: Text(recommendations[index].uid),
                                onTap: () {
                                  showModalBottomSheet(
                                      context: context,
                                      builder: (context) {
                                        return PageSheetInfo(
                                            page: recommendations[index]);
                                      });
                                },
                              ),
                            )),
                  ),
                )
              ],
            ),
    );
  }

  void fetchRecommendations() async {
    setState(() {
      isLoading = true;
    });
    var url = Uri.parse('http://127.0.0.1:5000/recuseralike');
    var body = jsonEncode({
      "already_watched": [],
      "worksheet_uids": (widget.chosenHistory.map((e) => e.uid).toList()),
      "cCode": "IL",
      "lCode": "he",
    });
    var headers = {"Content-Type": "application/json"};
    var response = await http.post(url, body: body, headers: headers);
    var data = List<dynamic>.empty(growable: true);
    if (response.statusCode == 200) {
      // If the server returns a 200 OK response, then parse the JSON.
      data = json.decode(response.body);

      setState(() {
        isLoading = false;
        recommendations = data.map((e) => MathCenterPage.fromJson(e)).toList();
      });
    } else {
      // If the server did not return a 200 OK response,
      // then throw an exception.
      log("${response.statusCode}");
    }
  }
}

class PageSheetInfo extends StatelessWidget {
  const PageSheetInfo({
    super.key,
    required this.page,
  });

  final MathCenterPage page;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            page.name,
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            'UID: ${page.uid}',
            style: const TextStyle(fontSize: 16),
          ),
          const SizedBox(height: 8),
          Text(
            'Grade Range: ${page.minGrade} - ${page.maxGrade}',
            style: const TextStyle(fontSize: 16),
          ),
          const SizedBox(height: 8),
          const Text(
            'Topics:',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          for (var topic in page.topics)
            Text(
              '- $topic',
              style: const TextStyle(fontSize: 16),
            ),
        ],
      ),
    );
  }
}
