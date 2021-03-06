#!/usr/bin/perl
use strict;

binmode STDOUT, ":utf8";

sub get_data_list {
	my $xpath = $_[0];
	my $query = $_[1];
	my $node = $_[2];
	my @nodes = $xpath->findnodes($query, $node);
	my @values;
	foreach (@nodes) {
		my $str = $_->getData();
		$str =~ s/[\n\r\t]+/ /g;
		if (!($str eq undef)) {
			push(@values, $str);
		}
	}
	return @values;
}

sub get_data_item {
	my @values = get_data_list($_[0], $_[1], $_[2]);
	return @values[0];
}

if (@ARGV == 0) {
	print STDERR "<xml file>\n";
	exit 1;
}

use XML::XPath;

foreach my $filename(@ARGV) {
	eval {
		my $xpath = XML::XPath->new(filename => $filename);
		my $nodes = $xpath->find('/eeml/environment');

		unless ($nodes->isa('XML::XPath::NodeSet')) {
			print STDERR "Query didn't return a nodeset. Value: ";
			print $nodes->value, "\n";
			exit 1;
		}
		if ($nodes->size) {
			# print STDERR "Found ", $nodes->size, " environments.\n";
			foreach my $node ($nodes->get_nodelist) {
				my $id = get_data_item($xpath, '@id', $node);
				
				my @streams = $xpath->findnodes('data', $node);
				foreach (@streams) {
					my $stream_id = get_data_item($xpath, '@id', $_);
					
					my @datapoints = $xpath->findnodes('datapoints/value', $_);
					foreach (@datapoints) {
						my $value = get_data_item($xpath, 'text()', $_);
						my $time = get_data_item($xpath, '@at', $_);
						print "${id}\t${stream_id}\t${time}\t${value}\n";
					}
				}
			}
		}
		else {
			print STDERR "No nodes found";
		}
	};
	if ($@) {
		print STDERR "An error occurred in file $filename: $@\n";
	}
}
