import 'package:flutter/material.dart';
import 'package:recui/mixed_model.dart';
import 'package:recui/user_similarity_page.dart';
import 'package:recui/markov_page.dart';
import 'package:recui/most_popular_page.dart';

class ChooseAlg extends StatelessWidget {
  const ChooseAlg({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Choose Algorithm"),
      ),
      body: Center(
        child: Column(children: [
          // User Similarity Button
          // TextButton(
          //   style: ButtonStyle(
          //     shape: MaterialStateProperty.all<RoundedRectangleBorder>(
          //       RoundedRectangleBorder(
          //         borderRadius: BorderRadius.circular(20),
          //       ),
          //     ),
          //     foregroundColor: MaterialStateProperty.all<Color>(Colors.pink),
          //   ),
          //   onPressed: () {
          //     Navigator.push(context,
          //         MaterialPageRoute(builder: (context) => const UserSimilarityPage()));
          //   },
          //   child: const Text('User Similarity'),
          // ),
          TextButton(
            style: ButtonStyle(
              shape: MaterialStateProperty.all<RoundedRectangleBorder>(
                RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                ),
              ),
              foregroundColor: MaterialStateProperty.all<Color>(Colors.pink),
            ),
            onPressed: () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (context) => const MostPopularPage()));
            },
            child: const Text('Most Popular'),
          ),
          TextButton(
            style: ButtonStyle(
              shape: MaterialStateProperty.all<RoundedRectangleBorder>(
                RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                ),
              ),
              foregroundColor: MaterialStateProperty.all<Color>(Colors.pink),
            ),
            onPressed: () {
              Navigator.push(context,
                  MaterialPageRoute(builder: (context) => const MixedPage()));
            },
            child: const Text('Mixed Model'),
          ),
        ]),
      ),
    );
  }
}
